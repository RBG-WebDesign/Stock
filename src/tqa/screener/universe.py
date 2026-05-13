# src/tqa/screener/universe.py
from typing import Any, Dict, List, Optional
import pandas as pd
from tqa.utils.logger import logger

class Screener:
    """
    Applies deterministic mathematical filters to market data to narrow down
    the universe to high-probability candidates.
    
    Uses a multi-stage "Waterfall" approach to discard weak candidates early.
    """
    def __init__(
        self, 
        min_eps_growth: float = 20.0,
        min_rev_growth: float = 20.0,
        min_prev_eps: Optional[float] = None,
        min_latest_eps: Optional[float] = None,
        require_acceleration: bool = False
    ):
        self.min_eps_growth = min_eps_growth
        self.min_rev_growth = min_rev_growth
        self.min_prev_eps = min_prev_eps
        self.min_latest_eps = min_latest_eps
        self.require_acceleration = require_acceleration

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
        if self.min_latest_eps is not None and eps_latest < self.min_latest_eps:
            return False

        eps_growth = ((eps_latest - eps_prev) / abs(eps_prev)) * 100
        
        # 2. Revenue Growth
        rev_latest = latest.get("revenue")
        rev_prev = prev.get("revenue")
        
        rev_growth = 0.0
        if rev_latest and rev_prev and rev_prev != 0:
            rev_growth = ((rev_latest - rev_prev) / rev_prev) * 100

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
        Waterfall Phase 2: Technical Filter (Trend Template).
        Requires at least 200+ days of historical data.
        """
        if not historical_data or len(historical_data) < 200:
            return False
            
        # Convert to DataFrame for easier indicator calculation
        df = pd.DataFrame(historical_data)
        # Data is newest to oldest, so we reverse it for rolling calculations
        df = df.iloc[::-1].reset_index(drop=True)
        
        closes = df["close"]
        highs = df["high"]
        lows = df["low"]
        
        # Calculate SMAs
        sma_50 = closes.rolling(window=50).mean()
        sma_100 = closes.rolling(window=100).mean()
        sma_200 = closes.rolling(window=200).mean()
        
        # Check for NaNs in the latest indicator values
        if pd.isna(sma_50.iloc[-1]) or pd.isna(sma_100.iloc[-1]) or pd.isna(sma_200.iloc[-1]):
            logger.debug("Technical failure: SMA indicators contain NaN.")
            return False

        curr_price = closes.iloc[-1]
        curr_sma_50 = sma_50.iloc[-1]
        curr_sma_100 = sma_100.iloc[-1]
        curr_sma_200 = sma_200.iloc[-1]
        
        # 52-Week Range
        last_252 = df.tail(252)
        low_52w = last_252["low"].min()
        high_52w = last_252["high"].max()
        
        # --- Trend Template Criteria ---
        
        # 1. Price > 100 SMA and Price > 200 SMA
        c1 = curr_price > curr_sma_100 and curr_price > curr_sma_200
        
        # 2. 100 SMA > 200 SMA
        c2 = curr_sma_100 > curr_sma_200
        
        # 3. 200 SMA is trending up for at least 1 month (approx 22-30 trading days)
        # We check if the 200 SMA today is higher than it was 22 days ago
        c3 = False
        if len(sma_200) >= 22:
            prev_sma_200 = sma_200.iloc[-22]
            if not pd.isna(prev_sma_200):
                c3 = curr_sma_200 > prev_sma_200
        
        # 4. 50 SMA > 100 SMA and 50 SMA > 200 SMA
        c4 = curr_sma_50 > curr_sma_100 and curr_sma_50 > curr_sma_200
        
        # 5. Price > 50 SMA
        c5 = curr_price > curr_sma_50
        
        # 6. Price is at least 30% above 52-week low
        c6 = curr_price >= (1.30 * low_52w)
        
        # 7. Price is within 25% of 52-week high
        c7 = curr_price >= (0.75 * high_52w)
        
        passed = all([c1, c2, c3, c4, c5, c6, c7])
        
        if not passed:
            logger.debug(f"Technical failure: c1={c1}, c2={c2}, c3={c3}, c4={c4}, c5={c5}, c6={c6}, c7={c7}")
            
        return passed

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
