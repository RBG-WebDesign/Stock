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

    async def fetch_institutional_positions(self, ticker: str) -> List[Dict[str, Any]]:
        """Fetches institutional ownership summary."""
        endpoint = "institutional-ownership/symbol-positions-summary"
        url = f"{self.BASE_URL}/{endpoint}"
        
        # This endpoint is restricted for starter plans.
        # We fetch it but only if plan is premium.
        # Calculate the most recent quarter likely to have 13F filings (45-day lag)
        now = datetime.now()
        report_date = now - timedelta(days=60)
        year = report_date.year
        quarter = (report_date.month - 1) // 3 + 1

        params = {
            "symbol": ticker.upper(),
            "year": str(year),
            "quarter": str(quarter)
        }
        data = await self.fetch_with_cache(
            endpoint_name="institutional-positions",
            ticker=ticker,
            url=url,
            params=params
        )
        return data if data else []

    async def fetch_earnings_surprises(self, ticker: str) -> List[Dict[str, Any]]:
        """Fetches recent earnings surprises."""
        endpoint = "earnings"
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
        return data if data else []

    async def fetch_analyst_estimates(self, ticker: str) -> List[Dict[str, Any]]:
        """Fetches analyst estimates for future EPS and revenue."""
        endpoint = "analyst-estimates"
        url = f"{self.BASE_URL}/{endpoint}"
        # Period 'annual' is less likely to be premium-only than 'quarter'
        params = {
            "symbol": ticker.upper(),
            "period": "annual",
            "limit": 8
        }
        data = await self.fetch_with_cache(
            endpoint_name=endpoint,
            ticker=ticker,
            url=url,
            params=params
        )
        return data if data else []

    async def fetch_stock_grades(self, ticker: str) -> List[Dict[str, Any]]:
        """Fetches latest stock grades/ratings from analysts."""
        endpoint = "grades"
        url = f"{self.BASE_URL}/{endpoint}"
        params = {"symbol": ticker.upper()}
        data = await self.fetch_with_cache(
            endpoint_name=endpoint,
            ticker=ticker,
            url=url,
            params=params
        )
        return data if data else []

    async def fetch_historical_stock_grades(self, ticker: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetches historical count of analyst buy/hold/sell ratings."""
        endpoint = "grades-historical"
        url = f"{self.BASE_URL}/{endpoint}"
        params = {"symbol": ticker.upper(), "limit": limit}
        data = await self.fetch_with_cache(
            endpoint_name=endpoint,
            ticker=ticker,
            url=url,
            params=params
        )
        return data if data else []

    async def fetch_historical_ratings(self, ticker: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Fetches historical financial ratings (DCF, ROE, etc. scores)."""
        endpoint = "ratings-historical"
        url = f"{self.BASE_URL}/{endpoint}"
        params = {"symbol": ticker.upper(), "limit": limit}
        data = await self.fetch_with_cache(
            endpoint_name=endpoint,
            ticker=ticker,
            url=url,
            params=params
        )
        return data if data else []

    async def fetch_financial_scores(self, ticker: str) -> Dict[str, Any]:
        """Fetches Altman Z-Score and Piotroski Score."""
        endpoint = "financial-scores"
        url = f"{self.BASE_URL}/{endpoint}"
        params = {"symbol": ticker.upper()}
        data = await self.fetch_with_cache(
            endpoint_name=endpoint,
            ticker=ticker,
            url=url,
            params=params
        )
        if data and isinstance(data, list):
            return data[0]
        return data if data else {}

    async def fetch_price_target_summary(self, ticker: str) -> Dict[str, Any]:
        """Fetches average analyst price targets."""
        endpoint = "price-target-summary"
        url = f"{self.BASE_URL}/{endpoint}"
        params = {"symbol": ticker.upper()}
        data = await self.fetch_with_cache(
            endpoint_name=endpoint,
            ticker=ticker,
            url=url,
            params=params
        )
        if data and isinstance(data, list):
            return data[0]
        return data if data else {}

    async def fetch_stock_news(self, ticker: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Fetches recent news articles for a specific ticker."""
        endpoint = "news/stock"
        url = f"{self.BASE_URL}/{endpoint}"
        params = {
            "symbols": ticker.upper(),
            "limit": limit
        }
        data = await self.fetch_with_cache(
            endpoint_name=endpoint,
            ticker=ticker,
            url=url,
            params=params
        )
        return data if data else []

    async def fetch_stock_price_change(self, ticker: str) -> Dict[str, Any]:
        """Fetches stock price change metrics."""
        endpoint = "stock-price-change"
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
            "stock_price_change": self.fetch_stock_price_change(ticker),
            "earnings_surprises": self.fetch_earnings_surprises(ticker),
            "stock_grades": self.fetch_stock_grades(ticker),
            "historical_grades": self.fetch_historical_stock_grades(ticker),
            "historical_ratings": self.fetch_historical_ratings(ticker),
            "financial_scores": self.fetch_financial_scores(ticker),
            "price_target_summary": self.fetch_price_target_summary(ticker),
            "news": self.fetch_stock_news(ticker, limit=settings.MAX_RECENT_ARTICLES),
            "historical": self.fetch_historical_prices(ticker)
        }
        
        # Only include premium endpoints if specified in settings
        if settings.FMP_PLAN == "premium":
            tasks["institutional_positions"] = self.fetch_institutional_positions(ticker)
            tasks["analyst_estimates"] = self.fetch_analyst_estimates(ticker)
        
        keys = list(tasks.keys())
        # return_exceptions=True prevents one failing call from crashing the whole gather
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        combined_data = {}
        for i, key in enumerate(keys):
            if isinstance(results[i], Exception):
                logger.error(f"Error fetching {key} for {ticker}: {results[i]}")
                combined_data[key] = [] if key != "share_float" else {}
            else:
                combined_data[key] = results[i]
        combined_data["ticker"] = ticker.upper()
        
        return combined_data
