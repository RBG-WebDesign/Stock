# src/tqa/data_fetchers/base.py
import asyncio
import io
import json
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, Type, TypeVar, List

import aiohttp
import pandas as pd
from config.settings import settings
from tqa.utils.logger import logger

T = TypeVar("T", bound="BaseDataFetcher")

class BaseDataFetcher(ABC):
    """
    Abstract Base Class for all external API data fetchers.
    Handles rate limiting, exponential backoff, and file-based caching.
    Supports being used as an async context manager for session cleanup.
    """

    def __init__(self, api_key: str, semaphore_limit: int = 10):
        self.api_key = api_key
        # Semaphore prevents 429 errors by limiting concurrent network requests
        self._semaphore = asyncio.Semaphore(semaphore_limit)
        self._session: Optional[aiohttp.ClientSession] = None
        self._cleanup_old_cache(days=settings.CACHE_CLEANUP_DAYS)

    async def __aenter__(self: T) -> T:
        await self._get_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def _get_session(self) -> aiohttp.ClientSession:
        """Ensures a single aiohttp session is used per fetcher instance."""
        if self._session is None or self._session.closed:
            # Setting a standard timeout for all requests
            timeout = aiohttp.ClientTimeout(total=30)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    async def close(self):
        """Closes the underlying aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()

    def _get_cache_path(self, endpoint_name: str, ticker: str) -> Path:
        """
        Constructs the standard path: data/raw/<endpoint>/TICKER_YYYY-MM-DD.json
        """
        today = datetime.now().strftime("%Y-%m-%d")
        # Clean endpoint and ticker names for filesystem
        clean_endpoint = endpoint_name.replace("/", "-").strip("-")
        clean_ticker = str(ticker).replace("/", "-").strip("-").upper()
        
        endpoint_dir = settings.RAW_DATA_DIR / clean_endpoint
        endpoint_dir.mkdir(parents=True, exist_ok=True)
        return endpoint_dir / f"{clean_ticker}_{today}.json"

    def _cleanup_old_cache(self, days: int) -> None:
        """
        Iterates through the RAW_DATA_DIR and deletes JSON files older than 'days'.
        Expects files to be in the format: TICKER_YYYY-MM-DD.json
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        logger.info(f"Cleaning up cache files older than {days} days (cutoff: {cutoff_date.date()})")

        count = 0
        try:
            # Recursively find all json files in the raw data directory
            for cache_file in settings.RAW_DATA_DIR.rglob("*.json"):
                try:
                    # Extract date from filename (e.g., AAPL_2023-01-01.json)
                    # We take the part after the last underscore and before .json
                    date_str = cache_file.stem.split("_")[-1]
                    file_date = datetime.strptime(date_str, "%Y-%m-%d")

                    if file_date < cutoff_date:
                        cache_file.unlink()
                        count += 1
                        logger.debug(f"Deleted old cache file: {cache_file.name}")
                except (ValueError, IndexError):
                    # Skip files that don't match our naming convention
                    continue
                except Exception as e:
                    logger.error(f"Error deleting cache file {cache_file}: {e}")

            if count > 0:
                logger.info(f"Cache cleanup complete. Deleted {count} files.")
        except Exception as e:
            logger.error(f"Error during cache cleanup: {e}")

    async def fetch_with_cache(
        self, 
        endpoint_name: str, 
        ticker: str, 
        url: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        The primary entry point for fetching data. 
        Checks the date-suffixed cache first before hitting the network.
        """
        cache_path = self._get_cache_path(endpoint_name, ticker)

        # 1. Check Cache
        if cache_path.exists():
            try:
                with open(cache_path, "r") as f:
                    logger.debug(f"Cache hit: {ticker} @ {endpoint_name}")
                    return json.load(f)
            except Exception as e:
                logger.error(f"Cache read error for {ticker}: {e}")

        # 2. Fetch from Network (Rate Limited)
        data = await self._make_request(url, params)

        # 3. Save to Cache
        if data is not None:
            try:
                with open(cache_path, "w") as f:
                    json.dump(data, f, indent=4)
                logger.debug(f"Cached new data: {ticker} @ {endpoint_name}")
            except Exception as e:
                logger.error(f"Cache write error for {ticker}: {e}")

        return data

    async def _make_request(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        retries: int = 8
    ) -> Any:
        """
        Executes a network request with a semaphore and exponential backoff.
        """
        session = await self._get_session()
        
        # Ensure API key is always included
        params = params or {}
        params["apikey"] = self.api_key

        for attempt in range(retries):
            async with self._semaphore:
                try:
                    logger.debug(f"Requesting: {url} (Attempt {attempt + 1})")
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            # Handle CSV if requested or if content type is CSV
                            is_csv_requested = params.get("datatype") == "csv"
                            content_type = response.headers.get("Content-Type", "")
                            
                            if is_csv_requested or "text/csv" in content_type:
                                csv_text = await response.text()
                                df = pd.read_csv(io.StringIO(csv_text))
                                # Replace NaN with None for JSON compatibility
                                data = df.where(pd.notnull(df), None).to_dict(orient="records")
                                return self._normalize_keys(data)
                            
                            return await response.json()
                        
                        # Retry on rate limits (429) or server errors (5xx)
                        if response.status == 429 or 500 <= response.status < 600:
                            # Exponential backoff with jitter
                            import random
                            base_wait = 2 ** (attempt + 1)
                            wait_time = base_wait + (random.random() * 0.5 * base_wait)
                            
                            status_msg = "Rate limited (429)" if response.status == 429 else f"Server error ({response.status})"
                            logger.warning(f"{status_msg}. Retrying in {wait_time:.2f}s... (Attempt {attempt + 1}/{retries})")
                            await asyncio.sleep(wait_time)
                            continue
                        
                        # Handle other HTTP errors (4xx other than 429)
                        error_text = await response.text()
                        logger.error(f"HTTP {response.status} for {url}: {error_text[:200]}")
                        
                        # If it's a non-retryable 4xx, return None
                        return None

                except asyncio.TimeoutError:
                    logger.error(f"Timeout on attempt {attempt + 1} for {url}")
                    await asyncio.sleep(2 ** attempt)
                except Exception as e:
                    logger.error(f"Network error on attempt {attempt + 1}: {e}")
                    await asyncio.sleep(2 ** attempt)

        return None

    def _normalize_keys(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Converts snake_case keys to camelCase for consistency with FMP JSON API."""

        def to_camel(snake_str):
            components = snake_str.split("_")
            return components[0] + "".join(x.title() for x in components[1:])

        normalized = []
        for item in data:
            normalized.append({to_camel(k): v for k, v in item.items()})
        return normalized

    @abstractmethod
    async def fetch_ticker_data(self, ticker: str) -> Dict[str, Any]:
        """
        To be implemented by specific providers (e.g. FMPClient).
        Should orchestrate calls to multiple endpoints and return a combined dict.
        """
        pass
