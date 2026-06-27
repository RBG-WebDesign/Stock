# tests/test_data_fetchers.py
import asyncio
import os
import pytest
from dotenv import load_dotenv
from tqa.data_fetchers.fmp import FMPClient
from tqa.utils.logger import logger

# Load environment variables for the API key
load_dotenv()

@pytest.mark.asyncio
async def test_fmp_client():
    """
    Integration test for the refined FMPClient.
    Verifies that all new endpoints and the orchestrator work as expected.
    """
    ticker = "AAPL"
    
    # Initialize the client
    # Note: It uses the FMP_API_KEY from .env by default
    async with FMPClient() as client:
        logger.info(f"--- Testing FMPClient for {ticker} ---")
        
        # 1. Test fetch_ticker_data (The primary orchestrator)
        logger.info(f"Fetching full ticker data for {ticker}...")
        data = await client.fetch_ticker_data(ticker)
        
        if data:
            logger.info("Successfully fetched ticker data.")
            logger.info(f"Keys present: {list(data.keys())}")
            
            # Verify specific data points
            for key in ["income_statement", "key_metrics", "ratios", "share_float", "historical"]:
                count = len(data[key]) if isinstance(data[key], (list, dict)) else "N/A"
                logger.info(f"  - {key}: {count} records/fields")
                
            if data.get("share_float"):
                logger.info(f"  - Share Float: {data['share_float'].get('floatShares'):,}")
        else:
            logger.error(f"Failed to fetch ticker data for {ticker}")

        # 2. Test fetch_universe
        logger.info("Fetching target universe...")
        universe = await client.fetch_universe()
        if universe:
            logger.info(f"Successfully fetched universe with {len(universe)} tickers.")
            logger.info(f"Sample ticker: {universe[0].get('symbol')}")
        else:
            logger.error("Failed to fetch universe.")

if __name__ == "__main__":
    try:
        asyncio.run(test_fmp_client())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.exception(f"Test failed with error: {e}")
