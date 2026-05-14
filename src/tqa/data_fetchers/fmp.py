# src/tqa/data_fetchers/fmp.py
import asyncio
import json
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

    def _proactive_cache_individual(self, endpoint: str, ticker: Any, data: Any):
        """
        Saves a piece of data into the local cache as if it were fetched individually.
        Ensures format compatibility (e.g. wrapping statements in a list).
        """
        if not ticker or not isinstance(ticker, str):
            logger.debug(f"Skipping proactive cache for {endpoint}: Invalid ticker {ticker}")
            return
            
        cache_path = self._get_cache_path(endpoint, ticker)
        if cache_path.exists():
            return

        # Wrap in list if it's an endpoint that usually returns a list (e.g. statements)
        list_endpoints = ["income-statement", "key-metrics", "ratios", "earnings"]
        if endpoint in list_endpoints and not isinstance(data, list):
            data = [data]

        try:
            with open(cache_path, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to proactively cache {ticker} for {endpoint}: {e}")

    async def fetch_universe(
        self,
        min_market_cap: int = settings.DEFAULT_MIN_MARKET_CAP,
        max_market_cap: int = settings.DEFAULT_MAX_MARKET_CAP
    ) -> List[Dict[str, Any]]:
        """
        Fetches the initial universe of stocks based on market cap and volume.
        
        Args:
            min_market_cap: Minimum market capitalization in absolute dollars.
            max_market_cap: Maximum market capitalization in absolute dollars.
        """
        endpoint = "company-screener"
        url = f"{self.BASE_URL}/{endpoint}"
        params = {
            "marketCapMoreThan": min_market_cap,
            "marketCapLowerThan": max_market_cap,
            "volumeMoreThan": 100000,
            "exchange": "NASDAQ,NYSE",
            "isActivelyTrading": "true",
            "limit": 10000  # Fetch a large pool to apply our own filters later
        }
        
        logger.info(f"Fetching target universe from FMP (${min_market_cap:,} to ${max_market_cap:,})...")
        
        # Unique cache key based on market cap range
        cache_ticker = f"UNIVERSE_{min_market_cap}_{max_market_cap}"
        
        data = await self.fetch_with_cache(
            endpoint_name=endpoint,
            ticker=cache_ticker,
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

    async def fetch_batch_quotes(self, tickers: List[str]) -> List[Dict[str, Any]]:
        """
        Fetches real-time quotes for a list of tickers in a single batch call.
        FMP supports up to 50 symbols per request.
        """
        if not tickers:
            return []
            
        chunk_size = 50
        chunks = [tickers[i:i + chunk_size] for i in range(0, len(tickers), chunk_size)]
        
        async def fetch_chunk(chunk):
            symbols = ",".join([t.upper() for t in chunk])
            endpoint = "quote"
            url = f"{self.BASE_URL}/{endpoint}/{symbols}"
            
            # We don't cache batch quotes as they are real-time and transient for screening
            session = await self._get_session()
            async with self._semaphore:
                async with session.get(url, params={"apikey": self.api_key}) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Batch quote fetch failed for {symbols}: {response.status}")
                        return []

        tasks = [fetch_chunk(chunk) for chunk in chunks]
        results = await asyncio.gather(*tasks)
        
        # Flatten the list of lists
        all_quotes = []
        for result in results:
            if isinstance(result, list):
                all_quotes.extend(result)
        
        return all_quotes

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

    async def fetch_company_profile(self, ticker: str) -> Dict[str, Any]:
        """Fetches detailed company profile (industry, description, CEO, etc.)."""
        endpoint = "profile"
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

    async def fetch_historical_prices(self, ticker: str, years: int = 4) -> List[Dict[str, Any]]:
        """Fetches OHLCV data for charting and local indicator calculation."""
        endpoint = "historical-price-eod/full"
        url = f"{self.BASE_URL}/{endpoint}"
        
        # Fetching 4 years by default to ensure we have enough data for 3-year weekly charts + leading SMAs
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

    async def fetch_income_statement_bulk(
        self,
        year: int,
        period: str,
        use_csv: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Fetches income statements for all companies for a given year and period.
        """
        endpoint = "income-statement-bulk"
        url = f"{self.BASE_URL}/{endpoint}"
        params = {
            "year": str(year),
            "period": period.upper()
        }
        if use_csv:
            params["datatype"] = "csv"
        
        # We use a special ticker "BULK" for caching bulk results
        suffix = "_CSV" if use_csv else ""
        ticker_key = f"BULK_{year}_{period.upper()}{suffix}"
        
        data = await self.fetch_with_cache(
            endpoint_name=endpoint,
            ticker=ticker_key,
            url=url,
            params=params
        )
        
        if data and isinstance(data, list):
            for statement in data:
                symbol = statement.get("symbol")
                if symbol:
                    self._proactive_cache_individual("income-statement", symbol, statement)

        return data if data else []

    async def fetch_earnings_surprises_bulk(self, year: int, use_csv: bool = False) -> List[Dict[str, Any]]:
        """
        Fetches annual earnings surprises for all companies for a given year.
        """
        endpoint = "earnings-surprises-bulk"
        url = f"{self.BASE_URL}/{endpoint}"
        params = {
            "year": str(year)
        }
        if use_csv:
            params["datatype"] = "csv"
        
        suffix = "_CSV" if use_csv else ""
        ticker_key = f"BULK_{year}{suffix}"
        
        data = await self.fetch_with_cache(
            endpoint_name=endpoint,
            ticker=ticker_key,
            url=url,
            params=params
        )
        if data and isinstance(data, list):
            for entry in data:
                symbol = entry.get("symbol")
                if symbol:
                    self._proactive_cache_individual("earnings", symbol, entry)
        return data if data else []

    async def fetch_balance_sheet_bulk(self, year: int, period: str, use_csv: bool = False) -> List[Dict[str, Any]]:
        """Fetches balance sheet statements for all companies."""
        endpoint = "balance-sheet-statement-bulk"
        url = f"{self.BASE_URL}/{endpoint}"
        params = {"year": str(year), "period": period.upper()}
        if use_csv:
            params["datatype"] = "csv"
        
        suffix = "_CSV" if use_csv else ""
        ticker_key = f"BULK_{year}_{period.upper()}{suffix}"
        
        return await self.fetch_with_cache(
            endpoint_name=endpoint,
            ticker=ticker_key,
            url=url,
            params=params
        )

    async def fetch_cash_flow_bulk(self, year: int, period: str, use_csv: bool = False) -> List[Dict[str, Any]]:
        """Fetches cash flow statements for all companies."""
        endpoint = "cash-flow-statement-bulk"
        url = f"{self.BASE_URL}/{endpoint}"
        params = {"year": str(year), "period": period.upper()}
        if use_csv:
            params["datatype"] = "csv"
        
        suffix = "_CSV" if use_csv else ""
        ticker_key = f"BULK_{year}_{period.upper()}{suffix}"
        
        return await self.fetch_with_cache(
            endpoint_name=endpoint,
            ticker=ticker_key,
            url=url,
            params=params
        )

    async def fetch_income_statement_growth_bulk(self, year: int, period: str, use_csv: bool = False) -> List[Dict[str, Any]]:
        """Fetches income statement growth for all companies."""
        endpoint = "income-statement-growth-bulk"
        url = f"{self.BASE_URL}/{endpoint}"
        params = {"year": str(year), "period": period.upper()}
        if use_csv:
            params["datatype"] = "csv"
        
        suffix = "_CSV" if use_csv else ""
        ticker_key = f"BULK_{year}_{period.upper()}{suffix}"
        
        return await self.fetch_with_cache(
            endpoint_name=endpoint,
            ticker=ticker_key,
            url=url,
            params=params
        )

    async def fetch_profile_bulk(self, part: int = 0, use_csv: bool = False) -> List[Dict[str, Any]]:
        """Fetches comprehensive company profiles in bulk."""
        endpoint = "profile-bulk"
        url = f"{self.BASE_URL}/{endpoint}"
        params = {"part": str(part)}
        if use_csv:
            params["datatype"] = "csv"
        
        suffix = "_CSV" if use_csv else ""
        ticker_key = f"PART_{part}{suffix}"
        
        data = await self.fetch_with_cache(
            endpoint_name=endpoint,
            ticker=ticker_key,
            url=url,
            params=params
        )
        if data and isinstance(data, list):
            for entry in data:
                symbol = entry.get("symbol")
                if symbol:
                    self._proactive_cache_individual("profile", symbol, entry)
        return data if data else []

    async def fetch_rating_bulk(self, use_csv: bool = False) -> List[Dict[str, Any]]:
        """Fetches stock ratings in bulk."""
        endpoint = "rating-bulk"
        url = f"{self.BASE_URL}/{endpoint}"
        params = {}
        if use_csv:
            params["datatype"] = "csv"
        
        suffix = "_CSV" if use_csv else ""
        ticker_key = f"ALL{suffix}"
        
        data = await self.fetch_with_cache(
            endpoint_name=endpoint,
            ticker=ticker_key,
            url=url,
            params=params
        )
        if data and isinstance(data, list):
            for entry in data:
                symbol = entry.get("symbol")
                if symbol:
                    self._proactive_cache_individual("rating", symbol, entry)
        return data if data else []

    async def fetch_scores_bulk(self, use_csv: bool = False) -> List[Dict[str, Any]]:
        """Fetches financial scores (Altman Z, Piotroski) in bulk."""
        endpoint = "scores-bulk"
        url = f"{self.BASE_URL}/{endpoint}"
        params = {}
        if use_csv:
            params["datatype"] = "csv"
        
        suffix = "_CSV" if use_csv else ""
        ticker_key = f"ALL{suffix}"
        
        data = await self.fetch_with_cache(
            endpoint_name=endpoint,
            ticker=ticker_key,
            url=url,
            params=params
        )
        if data and isinstance(data, list):
            for entry in data:
                symbol = entry.get("symbol")
                if symbol:
                    self._proactive_cache_individual("financial-scores", symbol, entry)
        return data if data else []

    async def fetch_price_target_summary_bulk(self, use_csv: bool = False) -> List[Dict[str, Any]]:
        """Fetches price target summaries in bulk."""
        endpoint = "price-target-summary-bulk"
        url = f"{self.BASE_URL}/{endpoint}"
        params = {}
        if use_csv:
            params["datatype"] = "csv"
        
        suffix = "_CSV" if use_csv else ""
        ticker_key = f"ALL{suffix}"
        
        data = await self.fetch_with_cache(
            endpoint_name=endpoint,
            ticker=ticker_key,
            url=url,
            params=params
        )
        if data and isinstance(data, list):
            for entry in data:
                symbol = entry.get("symbol")
                if symbol:
                    self._proactive_cache_individual("price-target-summary", symbol, entry)
        return data if data else []

    async def fetch_upgrades_downgrades_consensus_bulk(self, use_csv: bool = False) -> List[Dict[str, Any]]:
        """Fetches upgrades/downgrades consensus in bulk."""
        endpoint = "upgrades-downgrades-consensus-bulk"
        url = f"{self.BASE_URL}/{endpoint}"
        params = {}
        if use_csv:
            params["datatype"] = "csv"
        
        suffix = "_CSV" if use_csv else ""
        ticker_key = f"ALL{suffix}"
        
        data = await self.fetch_with_cache(
            endpoint_name=endpoint,
            ticker=ticker_key,
            url=url,
            params=params
        )
        if data and isinstance(data, list):
            for entry in data:
                symbol = entry.get("symbol")
                if symbol:
                    self._proactive_cache_individual("upgrades-downgrades-consensus", symbol, entry)
        return data if data else []

    async def fetch_market_cap_batch(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """Fetches market capitalization for multiple companies (batch)."""
        if not symbols:
            return []
            
        chunk_size = 50
        chunks = [symbols[i:i + chunk_size] for i in range(0, len(symbols), chunk_size)]
        
        async def fetch_chunk(chunk):
            syms = ",".join([s.upper() for s in chunk])
            endpoint = "market-capitalization-batch"
            url = f"{self.BASE_URL}/{endpoint}"
            params = {"symbols": syms, "apikey": self.api_key}
            
            session = await self._get_session()
            async with self._semaphore:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    return []

        tasks = [fetch_chunk(chunk) for chunk in chunks]
        results = await asyncio.gather(*tasks)
        
        all_data = []
        for r in results:
            if isinstance(r, list):
                all_data.extend(r)
        return all_data

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
            "historical": self.fetch_historical_prices(ticker),
            "profile": self.fetch_company_profile(ticker)
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
