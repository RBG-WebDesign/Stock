# src/tqa/screener/universe.py
from typing import Any, Dict, List
from tqa.utils.logger import logger

class Screener:
    """
    Applies deterministic mathematical filters to market data to narrow down
    the universe to high-probability candidates.
    """
    def __init__(self, min_eps_growth: float = 20.0):
        self.min_eps_growth = min_eps_growth

    def _check_eps_growth(self, income_statements: List[Dict[str, Any]]) -> bool:
        """
        Checks if the latest quarter's EPS grew by at least `min_eps_growth`% 
        compared to the previous quarter.
        """
        if not income_statements or len(income_statements) < 2:
            return False
        
        # FMP income statements are returned newest to oldest
        latest = income_statements[0]
        previous = income_statements[1]
        
        eps_latest = latest.get("eps")
        eps_prev = previous.get("eps")
        
        # Avoid division by zero or None types
        if eps_latest is None or eps_prev is None or eps_prev == 0:
            return False
            
        growth = ((eps_latest - eps_prev) / abs(eps_prev)) * 100
        return growth >= self.min_eps_growth

    def _check_technical(self, historical_data: List[Dict[str, Any]]) -> bool:
        """
        Checks if the current price is above the 50 SMA using historical prices.
        """
        if not historical_data or len(historical_data) < 50:
            return False
            
        # Data is sorted newest to oldest.
        last_50_closes = [day.get("close") for day in historical_data[:50]]
        
        if any(c is None for c in last_50_closes):
            return False
            
        sma = sum(last_50_closes) / 50
        latest_close = last_50_closes[0]
        
        return latest_close > sma

    def apply_filters(self, ticker_data: Dict[str, Any]) -> bool:
        """
        Evaluates a single ticker's full data payload against all criteria.
        Returns True if it passes, False otherwise.
        """
        ticker = ticker_data.get("ticker", "UNKNOWN")
        
        # 1. Fundamental Filter (EPS Growth)
        income_statements = ticker_data.get("income_statement", [])
        if not self._check_eps_growth(income_statements):
            return False
            
        # 2. Technical Filter (Price > 50 SMA)
        historical_data = ticker_data.get("historical", [])
        if not self._check_technical(historical_data):
            return False
            
        return True

    def screen(self, universe_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Takes a list of ticker data dicts and returns a filtered list.
        """
        passed = []
        for data in universe_data:
            if self.apply_filters(data):
                passed.append(data)
                logger.debug(f"Ticker {data.get('ticker')} passed all deterministic filters.")
                
        logger.info(f"Screening complete. {len(passed)}/{len(universe_data)} tickers survived.")
        return passed
