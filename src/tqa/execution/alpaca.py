# src/tqa/execution/alpaca.py
import asyncio
import json
from typing import Any, Dict, Optional
import aiohttp
from config.settings import settings
from tqa.utils.logger import logger

class AlpacaClient:
    """
    Asynchronous client for Alpaca API, enabling automated paper-trading execution.
    Supports bracket orders (buying at pivot with predefined stop-loss and take-profit).
    """

    def __init__(
        self,
        key_id: str = settings.ALPACA_API_KEY_ID,
        secret_key: str = settings.ALPACA_API_SECRET_KEY,
        base_url: str = settings.ALPACA_ENDPOINT
    ):
        self.key_id = key_id
        self.secret_key = secret_key
        self.base_url = base_url.rstrip('/')
        
        self.headers = {
            "APCA-API-KEY-ID": self.key_id,
            "APCA-API-SECRET-KEY": self.secret_key,
            "Content-Type": "application/json"
        }
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self._session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        if self._session:
            await self._session.close()
            self._session = None

    async def get_account_info(self) -> Optional[Dict[str, Any]]:
        """
        Fetches Alpaca account details to verify credentials and checking buying power.
        """
        url = f"{self.base_url}/account"
        logger.debug(f"Fetching Alpaca account information from {url}...")
        
        if not self.key_id or not self.secret_key:
            logger.error("Alpaca API credentials missing. Check your .env file.")
            return None

        try:
            session = self._session or aiohttp.ClientSession(headers=self.headers)
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info("Successfully authenticated with Alpaca API.")
                    return data
                else:
                    err_text = await response.text()
                    logger.error(f"Alpaca API error {response.status}: {err_text}")
                    return None
        except Exception as e:
            logger.error(f"Failed to fetch Alpaca account information: {e}")
            return None

    async def submit_bracket_order(
        self,
        symbol: str,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        qty: int
    ) -> Optional[Dict[str, Any]]:
        """
        Submits a bracket order (Buy Limit + Profit Target + Stop Loss) to the Alpaca API.
        """
        url = f"{self.base_url}/orders"
        
        payload = {
            "symbol": symbol.upper(),
            "qty": str(qty),
            "side": "buy",
            "type": "limit",
            "limit_price": f"{entry_price:.2f}",
            "time_in_force": "gtc",
            "order_class": "bracket",
            "take_profit": {
                "limit_price": f"{take_profit:.2f}"
            },
            "stop_loss": {
                "stop_price": f"{stop_loss:.2f}"
            }
        }
        
        logger.info(
            f"Submitting Alpaca bracket order for {symbol}: Buy {qty} shares @ Limit {entry_price:.2f} "
            f"(TP: {take_profit:.2f}, SL: {stop_loss:.2f})"
        )

        try:
            session = self._session or aiohttp.ClientSession(headers=self.headers)
            async with session.post(url, json=payload) as response:
                if response.status in [200, 201]:
                    order = await response.json()
                    logger.info(f"Successfully placed bracket order for {symbol}. Order ID: {order.get('id')}")
                    return order
                else:
                    err_text = await response.text()
                    logger.error(f"Failed to place bracket order for {symbol} (HTTP {response.status}): {err_text}")
                    return None
        except Exception as e:
            logger.error(f"Exception while placing Alpaca bracket order for {symbol}: {e}")
            return None
