import os
import time
import random
import requests
import pandas as pd
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv, find_dotenv

# --- CONFIGURATION ---
PROFILES_PATH = "data/company-profiles/company-profiles-bulk-usd-mktcap-cleaned.csv"
OUTPUT_DIR = "data/prices"
MARKET_CAP_THRESHOLD = 1_000_000_000 
MAX_WORKERS = 20  # As requested

DATE_CHUNKS = [
    ("1990-01-01", "2009-12-31"),
    ("2010-01-01", "2026-05-15")
]

# --- SETUP ---
load_dotenv(find_dotenv())
API_KEY = os.getenv("FMP_API_KEY")

def fetch_prices_with_backoff(symbol, start, end, max_retries=5):
    url = f"https://financialmodelingprep.com/stable/historical-price-eod/full"
    params = {"symbol": symbol, "from": start, "to": end, "apikey": API_KEY}
    
    for n in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                return pd.DataFrame(data) if data else pd.DataFrame()
            elif response.status_code == 429:
                # API Rate Limit - Back off heavily
                time.sleep((2 ** (n + 2)) + random.uniform(0, 1))
            elif 500 <= response.status_code < 600:
                time.sleep((2 ** (n + 1)) + random.uniform(0, 1))
            else:
                return pd.DataFrame()
        except Exception:
            time.sleep((2 ** (n + 1)) + random.uniform(0, 1))
    return pd.DataFrame()

def process_symbol(symbol):
    """Worker function to process a single symbol."""
    safe_symbol = str(symbol).replace(".", "_").replace("/", "_")
    first_char = safe_symbol[0].upper() if safe_symbol[0].isalpha() else "0-9"
    sub_dir = os.path.join(OUTPUT_DIR, first_char)
    
    # os.makedirs is thread-safe in Python 3.2+
    os.makedirs(sub_dir, exist_ok=True)
    file_path = os.path.join(sub_dir, f"{safe_symbol}.parquet")
    
    # Resumability check
    if os.path.exists(file_path):
        return f"Skipped {symbol}"
        
    all_chunks = []
    for start, end in DATE_CHUNKS:
        df_chunk = fetch_prices_with_backoff(symbol, start, end)
        if not df_chunk.empty:
            all_chunks.append(df_chunk)
            
    if all_chunks:
        full_history = pd.concat(all_chunks).drop_duplicates(subset=['date'])
        full_history['date'] = pd.to_datetime(full_history['date'])
        full_history = full_history.sort_values('date')
        full_history.to_parquet(file_path, index=False, engine='pyarrow', compression='snappy')
        return f"Downloaded {symbol}"
    
    return f"No Data {symbol}"

def main():
    if not os.path.exists(PROFILES_PATH):
        print(f"Error: Could not find {PROFILES_PATH}")
        return
    
    print(f"Loading and filtering symbols...")
    df_profiles = pd.read_csv(PROFILES_PATH)
    df_filtered = df_profiles[df_profiles['marketCapUSD'] >= MARKET_CAP_THRESHOLD].copy()
    symbols = df_filtered['symbol'].unique()
    
    print(f"Targeting {len(symbols)} symbols with {MAX_WORKERS} workers...")

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