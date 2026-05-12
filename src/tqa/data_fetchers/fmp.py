# src/tqa/data_fetchers/fmp.py
import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from config.settings import settings
from tqa.data_fetchers.base import BaseDataFetcher
from tqa.utils.logger import logger

class FMPClient(BaseDataFetcher):
    """
    Financial Modeling Prep API Client.
    Fetches the stock universe, fundamental metrics, and technical data.
    """
    BASE_URL = "https://financialmodelingprep.com/stable"

    def __init__(self, api_key: Optional[str] = None, semaphore_limit: int = 10):
        # Use provided key or fallback to settings
        key = api_key or settings.FMP_API_KEY
        super().__init__(api_key=key, semaphore_limit=semaphore_limit)

    async def fetch_universe(self) -> List[Dict[str, Any]]:
        """
        Fetches the initial universe of stocks based on market cap and volume.
        """
        endpoint = "company-screener"
        url = f"{self.BASE_URL}/{endpoint}"
        params = {
            "marketCapMoreThan": 100000000,     # $100M
            "marketCapLowerThan": 1000000000,   # $1B
            "volumeMoreThan": 100000,
            "exchange": "NASDAQ,NYSE",
            "isActivelyTrading": "true",
            "limit": 10000  # Fetch a large pool to apply our own filters later
        }
        
        logger.info("Fetching target universe from FMP...")
        # Use "UNIVERSE" as a pseudo-ticker for caching the screener results
        data = await self.fetch_with_cache(
            endpoint_name=endpoint,
            ticker="UNIVERSE",
            url=url,
            params=params
        )
        return data if data else []

    async def fetch_income_statement(self, ticker: str, limit: int = 8) -> List[Dict[str, Any]]:
        """Fetches quarterly income statements for EPS and revenue growth analysis."""
        endpoint = "income-statement"
        url = f"{self.BASE_URL}/{endpoint}"
        params = {
            "symbol": ticker.upper(),
            "period": "quarter",
            "limit": limit
        }
        data = await self.fetch_with_cache(
            endpoint_name=endpoint,
            ticker=ticker,
            url=url,
            params=params
        )
        return data if data else []

    async def fetch_key_metrics(self, ticker: str, limit: int = 8) -> List[Dict[str, Any]]:
        """Fetches key metrics like ROE, ROIC, and Net Debt."""
        endpoint = "key-metrics"
        url = f"{self.BASE_URL}/{endpoint}"
        params = {
            "symbol": ticker.upper(),
            "period": "annual",  # Quarter is premium for some users
            "limit": limit
        }
        data = await self.fetch_with_cache(
            endpoint_name=endpoint,
            ticker=ticker,
            url=url,
            params=params
        )
        return data if data else []

    async def fetch_financial_ratios(self, ticker: str, limit: int = 8) -> List[Dict[str, Any]]:
        """Fetches financial ratios like margins (gross, operating, net)."""
        endpoint = "ratios"
        url = f"{self.BASE_URL}/{endpoint}"
        params = {
            "symbol": ticker.upper(),
            "period": "annual",  # Quarter is premium for some users
            "limit": limit
        }
        data = await self.fetch_with_cache(
            endpoint_name=endpoint,
            ticker=ticker,
            url=url,
            params=params
        )
        return data if data else []

    async def fetch_share_float(self, ticker: str) -> Dict[str, Any]:
        """Fetches share float data for supply/demand analysis."""
        endpoint = "shares-float"
        url = f"{self.BASE_URL}/{endpoint}"
        params = {
            "symbol": ticker.upper()
        }
        data = await self.fetch_with_cache(
            endpoint_name=endpoint,
            ticker=ticker,
            url=url,
            params=params
        )
        # Returns a list of one item
        if data and isinstance(data, list):
            return data[0]
        return data if data else {}

    async def fetch_historical_prices(self, ticker: str, years: int = 2) -> List[Dict[str, Any]]:
        """Fetches OHLCV data for charting and local indicator calculation."""
        endpoint = "historical-price-eod/full"
        url = f"{self.BASE_URL}/{endpoint}"
        
        # Fetching 2 years by default to ensure we have enough data for long-term SMAs and Weekly charts
        start_date = (datetime.now() - timedelta(days=365 * years)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        params = {
            "symbol": ticker.upper(),
            "from": start_date,
            "to": end_date
        }
        
        data = await self.fetch_with_cache(
            endpoint_name="historical-price",
            ticker=ticker,
            url=url,
            params=params
        )
        
        # The EOD endpoint returns data inside a 'historical' key
        if data and isinstance(data, dict) and "historical" in data:
            return data["historical"]
        return data if isinstance(data, list) else []

    async def fetch_ticker_data(self, ticker: str) -> Dict[str, Any]:
        """
        Orchestrates fetching all required data (fundamentals + technicals) for a given ticker concurrently.
        """
        logger.debug(f"Fetching comprehensive data for {ticker}...")
        
        # Run all network calls concurrently for this ticker
        tasks = {
            "income_statement": self.fetch_income_statement(ticker),
            "key_metrics": self.fetch_key_metrics(ticker),
            "ratios": self.fetch_financial_ratios(ticker),
            "share_float": self.fetch_share_float(ticker),
            "historical": self.fetch_historical_prices(ticker)
        }
        
        keys = list(tasks.keys())
        results = await asyncio.gather(*tasks.values())
        
        combined_data = {keys[i]: results[i] for i in range(len(keys))}
        combined_data["ticker"] = ticker.upper()
        
        return combined_data
