# tests/test_charting.py
import json
import os
from tqa.charting.builder import ChartBuilder
from tqa.utils.logger import logger

def test_chart_generation():
    """
    Tests the ChartBuilder using cached historical data.
    """
    ticker = "AAPL"
    
    # Look for the most recent cached historical data file for the ticker
    import glob
    pattern = f"data/raw/historical-price/{ticker}_*.json"
    cache_files = sorted(glob.glob(pattern), reverse=True)
    
    if not cache_files:
        logger.error(f"No cache files found for {ticker} in data/raw/historical-price/. Run test_data_fetchers.py first.")
        return

    cache_path = cache_files[0]
    logger.info(f"Loading historical data from {cache_path}...")
    with open(cache_path, 'r') as f:
        # FMP historical endpoint returns data in a 'historical' key OR as a list
        data = json.load(f)
        if isinstance(data, dict) and "historical" in data:
            historical_data = data["historical"]
        else:
            historical_data = data

    builder = ChartBuilder(output_dir="data/charts/test")
    
    logger.info(f"Building charts for {ticker}...")
    results = builder.build_all(ticker, historical_data)
    
    if "daily" in results:
        logger.info(f"Daily chart generated: {results['daily']}")
        assert os.path.exists(results["daily"])
    else:
        logger.error("Failed to generate daily chart.")
        
    if "weekly" in results:
        logger.info(f"Weekly chart generated: {results['weekly']}")
        assert os.path.exists(results["weekly"])
    else:
        logger.error("Failed to generate weekly chart.")

if __name__ == "__main__":
    test_chart_generation()
