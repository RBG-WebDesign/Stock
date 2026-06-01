import os
import time
import random
import requests
import pandas as pd
from datetime import datetime, timedelta
from tqdm.auto import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv, find_dotenv

# --- CONFIGURATION ---
# Set to None to process all exchanges from the CSV file
TARGET_EXCHANGE = None 
# Local CSV path for full stock list fallback
PROFILES_CSV_PATH = "/opt/rws/data/fmp/fmp-company-profiles.csv"
# Professional absolute path as requested
OUTPUT_DIR = "/home/vince/repos/techno-quantamental-analyzer/notebooks/fmp-full-download/data/historical-market-cap"
GLOBAL_START_DATE = "1990-01-01"
MAX_WORKERS = 50
LIMIT_PER_REQUEST = 5000
CHUNK_SIZE_YEARS = 13
OVERWRITE = False  # Set to True to re-download everything from scratch

# --- SETUP ---
load_dotenv(find_dotenv())
API_KEY = os.getenv("FMP_API_KEY")
BASE_URL = "https://financialmodelingprep.com/stable"
TODAY = datetime.now().strftime('%Y-%m-%d')

def get_date_chunks(start_str, end_str):
    """Generates chunks of ~13 years between start and end."""
    chunks = []
    start_dt = datetime.strptime(start_str, '%Y-%m-%d')
    end_dt = datetime.strptime(end_str, '%Y-%m-%d')
    
    curr_end = end_dt
    while curr_end >= start_dt:
        curr_start = curr_end - timedelta(days=CHUNK_SIZE_YEARS * 365)
        if curr_start < start_dt:
            curr_start = start_dt
            
        chunks.append((curr_start.strftime('%Y-%m-%d'), curr_end.strftime('%Y-%m-%d')))
        curr_end = curr_start - timedelta(days=1)
        
    return chunks

# Pre-calculate global chunks once for all stocks
GLOBAL_CHUNKS = get_date_chunks(GLOBAL_START_DATE, TODAY)

def fetch_mktcap_batch(symbol, start, end, max_retries=5):
    """Fetches a single batch of market cap data for a specific date range."""
    url = f"{BASE_URL}/historical-market-capitalization"
    params = {
        "symbol": symbol,
        "from": start,
        "to": end,
        "limit": LIMIT_PER_REQUEST,
        "apikey": API_KEY
    }
    
    for n in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                return pd.DataFrame(data) if data else pd.DataFrame()
            elif response.status_code == 429:
                # Rate limit hit - exponential backoff
                time.sleep((2 ** (n + 2)) + random.uniform(0, 1))
            else:
                return pd.DataFrame()
        except Exception:
            time.sleep((2 ** (n + 1)) + random.uniform(0, 1))
    return pd.DataFrame()

def process_symbol(symbol):
    """Worker function to process a single symbol incrementally."""
    safe_symbol = str(symbol).replace(".", "_").replace("/", "_")
    first_char = safe_symbol[0].upper() if safe_symbol[0].isalpha() else "0-9"
    sub_dir = os.path.join(OUTPUT_DIR, first_char)
    os.makedirs(sub_dir, exist_ok=True)
    file_path = os.path.join(sub_dir, f"{safe_symbol}.parquet")
    
    existing_df = pd.DataFrame()
    if os.path.exists(file_path) and not OVERWRITE:
        try:
            existing_df = pd.read_parquet(file_path)
            existing_df['date'] = pd.to_datetime(existing_df['date'])
        except Exception:
            existing_df = pd.DataFrame()

    new_data_frames = []
    
    if existing_df.empty:
        # Full range download using pre-calculated chunks
        for s, e in GLOBAL_CHUNKS:
            new_data_frames.append(fetch_mktcap_batch(symbol, s, e))
    else:
        min_c = existing_df['date'].min().strftime('%Y-%m-%d')
        max_c = existing_df['date'].max().strftime('%Y-%m-%d')
        
        # Gap 1: Fetch older data (before cached range)
        if min_c > GLOBAL_START_DATE:
            end_gap = (datetime.strptime(min_c, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
            gap_chunks = get_date_chunks(GLOBAL_START_DATE, end_gap)
            for s, e in gap_chunks:
                new_data_frames.append(fetch_mktcap_batch(symbol, s, e))
                
        # Gap 2: Fetch newer data (after cached range)
        if max_c < TODAY:
            start_gap = (datetime.strptime(max_c, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
            gap_chunks = get_date_chunks(start_gap, TODAY)
            for s, e in gap_chunks:
                new_data_frames.append(fetch_mktcap_batch(symbol, s, e))
                
    # Filter out empty results
    new_data_frames = [df for df in new_data_frames if not df.empty]
    
    if new_data_frames:
        # Merge, deduplicate, and sort
        combined_df = pd.concat([existing_df] + new_data_frames, ignore_index=True)
        combined_df['date'] = pd.to_datetime(combined_df['date'])
        combined_df = combined_df.drop_duplicates(subset=['date']).sort_values('date', ascending=False)
        combined_df.to_parquet(file_path, index=False, engine='pyarrow', compression='snappy')
        return f"Updated {symbol} (+{len(new_data_frames)} batches)"
    
    return f"Up to date {symbol}"

def get_symbols():
    """Determines the target list of symbols based on config."""
    if TARGET_EXCHANGE:
        print(f"Targeting exchange: {TARGET_EXCHANGE}")
        url = f"{BASE_URL}/company-screener"
        params = {"exchange": TARGET_EXCHANGE, "apikey": API_KEY, "limit": 10000}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return pd.DataFrame(response.json())['symbol'].unique()
        except Exception as e:
            print(f"Error fetching symbols from API: {e}")
            return []
    else:
        print(f"No exchange specified. Falling back to full list from: {PROFILES_CSV_PATH}")
        if os.path.exists(PROFILES_CSV_PATH):
            df = pd.read_csv(PROFILES_CSV_PATH)
            if 'symbol' in df.columns:
                return df['symbol'].unique()
            else:
                print("Error: 'symbol' column not found in CSV.")
                return []
        else:
            print(f"Error: CSV file not found at {PROFILES_CSV_PATH}")
            return []

def main():
    print(f"--- Historical Market Cap Downloader ---")
    print(f"Start Date:      {GLOBAL_START_DATE}")
    print(f"Output Dir:      {OUTPUT_DIR}")
    print(f"Overwrite:       {OVERWRITE}")
    print(f"Max Workers:     {MAX_WORKERS}")
    print(f"----------------------------------------")

    # 1. Get Symbols
    symbols = get_symbols()
    if len(symbols) == 0:
        print("No symbols to process.")
        return
        
    print(f"Found {len(symbols)} symbols. Starting parallel download...")

    # 2. Parallel Processing
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_symbol, s): s for s in symbols}
        
        # tqdm for professional progress reporting
        with tqdm(total=len(symbols), desc="Download Progress") as pbar:
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    sym = futures[future]
                    print(f"\n[ERROR] {sym}: {e}")
                pbar.update(1)

    print(f"\nDownload complete. Data saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
