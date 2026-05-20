import os
import time
import random
import requests
import pandas as pd
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv, find_dotenv

# --- CONFIGURATION ---
# Path to the filtered company profiles CSV
PROFILES_PATH = "data/company-profiles/company-profiles-bulk-usd-mktcap-cleaned.csv"
# Directory where 30-minute parquet files will be stored
OUTPUT_DIR = "data/prices-30min"
# Minimum market cap in USD (1 Billion)
MARKET_CAP_THRESHOLD = 1_000_000_000 
# Concurrent workers for API requests
MAX_WORKERS = 20
# Set to True to re-download existing files
OVERWRITE = True 

# --- DATE RANGE ---
# Working backwards from the requested end date
END_DATE = "2026-05-31" 
# Going back as far as 1990 if data is available
START_LIMIT = "1990-01-01"
# Interval for each request. FMP intraday APIs often limit results to ~1 month.
CHUNK_DAYS = 30

# --- SETUP ---
load_dotenv(find_dotenv())
API_KEY = os.getenv("FMP_API_KEY")

def fetch_prices_with_backoff(symbol, start, end, max_retries=5):
    """Fetch 30-minute historical chart data with exponential backoff."""
    # Endpoint for 30-minute interval stock chart
    url = f"https://financialmodelingprep.com/stable/historical-chart/30min"
    params = {"symbol": symbol, "from": start, "to": end, "apikey": API_KEY}
    
    for n in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                # The 30min API returns a list of dictionaries directly
                return pd.DataFrame(data) if data else pd.DataFrame()
            elif response.status_code == 429:
                # API Rate Limit - Back off heavily
                time.sleep((2 ** (n + 2)) + random.uniform(0, 1))
            elif 500 <= response.status_code < 600:
                # Server error - Back off
                time.sleep((2 ** (n + 1)) + random.uniform(0, 1))
            else:
                # Other errors (e.g. 404, 403) - Return empty
                return pd.DataFrame()
        except Exception:
            # Connection errors etc. - Back off
            time.sleep((2 ** (n + 1)) + random.uniform(0, 1))
    return pd.DataFrame()

def process_symbol(symbol):
    """Worker function to process a single symbol backwards in time."""
    safe_symbol = str(symbol).replace(".", "_").replace("/", "_")
    first_char = safe_symbol[0].upper() if safe_symbol[0].isalpha() else "0-9"
    sub_dir = os.path.join(OUTPUT_DIR, first_char)
    
    # os.makedirs is thread-safe in Python 3.2+
    os.makedirs(sub_dir, exist_ok=True)
    file_path = os.path.join(sub_dir, f"{safe_symbol}.parquet")
    
    # Resumability check
    if os.path.exists(file_path) and not OVERWRITE:
        return f"Skipped {symbol}"
        
    all_chunks = []
    current_end = pd.to_datetime(END_DATE)
    limit_date = pd.to_datetime(START_LIMIT)
    
    # Loop backwards from END_DATE until we hit START_LIMIT or the API stops returning data
    while current_end >= limit_date:
        current_start = current_end - pd.Timedelta(days=CHUNK_DAYS)
        if current_start < limit_date:
            current_start = limit_date
            
        df_chunk = fetch_prices_with_backoff(
            symbol, 
            current_start.strftime('%Y-%m-%d'), 
            current_end.strftime('%Y-%m-%d')
        )
        
        if df_chunk.empty:
            # If a request returns no data, we've likely hit the end of the available historical record
            break
            
        all_chunks.append(df_chunk)
        
        # Move the window back for the next iteration
        current_end = current_start - pd.Timedelta(days=1)
            
    if all_chunks:
        # Concatenate all collected blocks
        full_history = pd.concat(all_chunks).drop_duplicates(subset=['date'])
        # Ensure date is in datetime format and sorted chronologically
        full_history['date'] = pd.to_datetime(full_history['date'])
        full_history = full_history.sort_values('date')
        # Save as parquet
        full_history.to_parquet(file_path, index=False, engine='pyarrow', compression='snappy')
        return f"Downloaded {symbol} ({len(all_chunks)} chunks)"
    
    return f"No Data {symbol}"

def main():
    if not os.path.exists(PROFILES_PATH):
        print(f"Error: Could not find {PROFILES_PATH}")
        return
    
    print(f"Loading and filtering symbols from {PROFILES_PATH}...")
    df_profiles = pd.read_csv(PROFILES_PATH)
    
    if 'marketCapUSD' not in df_profiles.columns:
        print(f"Error: 'marketCapUSD' column missing from {PROFILES_PATH}")
        return
        
    df_filtered = df_profiles[df_profiles['marketCapUSD'] >= MARKET_CAP_THRESHOLD].copy()
    symbols = df_filtered['symbol'].unique()
    
    print(f"Targeting {len(symbols)} symbols with {MAX_WORKERS} workers...")
    print(f"Downloading backwards from {END_DATE} to {START_LIMIT} in {CHUNK_DAYS}-day increments.")
    if OVERWRITE:
        print("OVERWRITE is enabled. Existing files will be replaced.")
    else:
        print("OVERWRITE is disabled. Existing files will be skipped.")

    # Use ThreadPoolExecutor for I/O bound API tasks
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all tasks and create a mapping of future to symbol
        future_to_symbol = {executor.submit(process_symbol, s): s for s in symbols}
        
        # Use tqdm to track completion
        for future in tqdm(as_completed(future_to_symbol), total=len(symbols), desc="Total Progress"):
            try:
                result = future.result()
            except Exception as e:
                symbol = future_to_symbol[future]
                print(f"\n[!] Symbol {symbol} generated an exception: {e}")

if __name__ == "__main__":
    main()
