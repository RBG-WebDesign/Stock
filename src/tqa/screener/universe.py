# src/tqa/screener/universe.py
from typing import Any, Dict, List, Optional
import pandas as pd
import re
from tqa.utils.logger import logger
from config.settings import settings

class Screener:
    """
    Applies deterministic mathematical filters to market data to narrow down
    the universe to high-probability candidates.
    
    Uses a multi-stage "Waterfall" approach to discard weak candidates early.
    """
    def __init__(
        self,
        min_eps_growth: float = settings.DEFAULT_MIN_EPS_GROWTH,
        min_rev_growth: float = settings.DEFAULT_MIN_REV_GROWTH,
        max_rev_growth: Optional[float] = None,
        min_prev_eps: Optional[float] = None,
        max_prev_eps: Optional[float] = None,
        min_latest_eps: Optional[float] = None,
        require_acceleration: bool = False,
        technical_filters: Optional[List[str]] = None
    ):
        self.min_eps_growth = min_eps_growth
        self.min_rev_growth = min_rev_growth
        self.max_rev_growth = max_rev_growth
        self.min_prev_eps = min_prev_eps
        self.max_prev_eps = max_prev_eps
        self.min_latest_eps = min_latest_eps
        self.require_acceleration = require_acceleration
        # Default to Mark Minervini's Trend Template if no filters provided
        self.technical_filters = technical_filters or [
            "price > sma_100",
            "price > sma_200",
            "sma_100 > sma_200",
            "sma_200 > sma_200_22d",
            "sma_50 > sma_100",
            "sma_50 > sma_200",
            "price > sma_50",
            "price >= 1.30 * low_52w",
            "price >= 0.75 * high_52w"
        ]

    def check_fundamentals(self, income_statements: List[Dict[str, Any]]) -> bool:
        """
        Waterfall Phase 1: Fundamental Filter.
        Checks for EPS and Revenue growth.
        """
        if not income_statements or len(income_statements) < 2:
            return False
        
        # FMP income statements are returned newest to oldest
        latest = income_statements[0]
        prev = income_statements[1]
        
        # 1. EPS Growth
        eps_latest = latest.get("eps")
        eps_prev = prev.get("eps")
        
        if eps_latest is None or eps_prev is None or eps_prev == 0:
            return False
            
        # Optional absolute EPS filters
        if self.min_prev_eps is not None and eps_prev < self.min_prev_eps:
            return False
        if self.max_prev_eps is not None and eps_prev > self.max_prev_eps:
            return False
        if self.min_latest_eps is not None and eps_latest < self.min_latest_eps:
            return False

        eps_growth = ((eps_latest - eps_prev) / abs(eps_prev)) * 100
        
        # 2. Revenue Growth
        rev_latest = latest.get("revenue")
        rev_prev = prev.get("revenue")
        
        rev_growth = 0.0
        if rev_latest and rev_prev and rev_prev != 0:
            rev_growth = ((rev_latest - rev_prev) / rev_prev) * 100

        # Optional revenue growth limit
        if self.max_rev_growth is not None and rev_growth > self.max_rev_growth:
            return False

        # Acceleration Check (Optional)
        if self.require_acceleration and len(income_statements) >= 3:
            prev_prev = income_statements[2]
            eps_prev_prev = prev_prev.get("eps")
            if eps_prev_prev and eps_prev_prev != 0:
                prev_growth = ((eps_prev - eps_prev_prev) / abs(eps_prev_prev)) * 100
                if eps_growth <= prev_growth:
                    return False

        return eps_growth >= self.min_eps_growth and rev_growth >= self.min_rev_growth

    def check_technicals(self, historical_data: List[Dict[str, Any]]) -> bool:
        """
        Waterfall Phase 2: Technical Filter.
        Evaluates dynamic filters against historical price data.
        """
        if not historical_data:
            logger.debug("Technical check failed: No historical data provided.")
            return False
            
        if len(historical_data) < 252:
            # We need at least 252 days for 52-week highs/lows
            logger.debug(f"Technical check failed: Insufficient historical data ({len(historical_data)} days).")
            return False
            
        try:
            # Convert to DataFrame for easier indicator calculation
            df = pd.DataFrame(historical_data)
            # Data is newest to oldest, so we reverse it for rolling calculations
            df = df.iloc[::-1].reset_index(drop=True)
            
            # Basic validation of required columns
            required_cols = {"close", "low", "high", "volume"}
            missing = required_cols - set(df.columns)
            if missing:
                logger.error(f"Technical check failed: Missing columns {missing}")
                return False

            # Standard Indicators Calculation
            df["price"] = df["close"]
            
            # Dynamically discover requested SMA windows from the filters
            requested_windows = {10, 20, 50, 100, 150, 200} # Default set
            for condition in self.technical_filters:
                matches = re.findall(r"sma_(\d+)", condition)
                for m in matches:
                    requested_windows.add(int(m))
            
            for window in requested_windows:
                df[f"sma_{window}"] = df["close"].rolling(window=window).mean()
                # Historical trend value (1 month ago / 22 trading days)
                df[f"sma_{window}_22d"] = df[f"sma_{window}"].shift(22)
                
            # 52-Week Range
            df["low_52w"] = df["low"].rolling(window=252).min()
            df["high_52w"] = df["high"].rolling(window=252).max()
            
            # Volume Indicators
            df["vol_avg_20"] = df["volume"].rolling(window=20).mean()

        except Exception as e:
            logger.error(f"Error calculating technical indicators: {e}")
            return False

        # Evaluate all dynamic filters
        for condition in self.technical_filters:
            try:
                # Use pandas eval on the entire dataframe to generate a boolean series,
                # then check the value for the latest row.
                results = df.eval(condition)
                
                # If results is a Series, get the last value. If it's a scalar, it's a constant.
                if isinstance(results, pd.Series):
                    # Check if the result is valid (not NaN) and Truthy
                    val = results.iloc[-1]
                    if pd.isna(val) or not val:
                        logger.debug(f"Technical failure: Condition '{condition}' failed for latest row.")
                        return False
                elif not results:
                    logger.debug(f"Technical failure: Condition '{condition}' evaluated to False.")
                    return False
            except Exception as e:
                # Log the specific condition that failed and the error, but return False instead of crashing
                logger.error(f"Error evaluating technical filter '{condition}': {e}")
                return False
                
        return True

    def apply_filters(self, ticker_data: Dict[str, Any]) -> bool:
        """
        Evaluates a single ticker's data payload.
        Assumes data is already fetched.
        """
        # Phase 1: Fundamentals
        if not self.check_fundamentals(ticker_data.get("income_statement", [])):
            return False
            
        # Phase 2: Technicals
        if not self.check_technicals(ticker_data.get("historical", [])):
            return False
            
        return True

    def screen(self, universe_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filters a list of ticker data.
        """
        passed = []
        for data in universe_data:
            if self.apply_filters(data):
                passed.append(data)
                
        logger.info(f"Screening complete. {len(passed)}/{len(universe_data)} survived.")
        return passed
