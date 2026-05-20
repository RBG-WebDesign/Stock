import os
import time
import random
import requests
import pandas as pd
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

from dotenv import load_dotenv, find_dotenv
from rich.live import Live
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn, TaskProgressColumn
from rich.console import Group
from rich.panel import Panel

# --- CONFIGURATION ---
PROFILES_PATH = "data/company-profiles/company-profiles-bulk-usd-mktcap-cleaned.csv"
OUTPUT_DIR = "data/news"
MARKET_CAP_THRESHOLD = 1_000_000_000 
MAX_WORKERS = 8 
NEWS_LIMIT_PER_PAGE = 250 

load_dotenv(find_dotenv())
API_KEY = os.getenv("FMP_API_KEY")

# Thread-safe state tracking
state_lock = Lock()
worker_status = {}  # { symbol: { "status": str, "date": str, "count": int } }

def fetch_news_batch(symbol, target_from, target_to, page, max_retries=5):
    url = "https://financialmodelingprep.com/stable/news/stock"
    # Ensure date parameters are strictly YYYY-MM-DD
    params = {
        "symbols": symbol,
        "from": target_from.split(' ')[0],
        "to": target_to.split(' ')[0],
        "page": page,
        "limit": NEWS_LIMIT_PER_PAGE,
        "apikey": API_KEY
    }
    
    for n in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                time.sleep((2 ** n) + random.uniform(0, 1))
            else:
                return []
        except:
            time.sleep(1)
    return []

def process_symbol_news(symbol, global_from="1990-01-01", global_to="2026-05-15"):
    safe_symbol = str(symbol).replace(".", "_").replace("/", "_")
    sub_dir = os.path.join(OUTPUT_DIR, safe_symbol[0].upper() if safe_symbol[0].isalpha() else "0-9")
    os.makedirs(sub_dir, exist_ok=True)
    file_path = os.path.join(sub_dir, f"{safe_symbol}.parquet")
    
    if os.path.exists(file_path):
        with state_lock:
            worker_status[symbol] = {"status": "[grey70]Skipped[/]", "date": "-", "count": 0}
        return

    all_news = []
    seen_urls = set()
    current_to = global_to
    page = 0
    last_slid_date = None

    while True:
        data = fetch_news_batch(symbol, global_from, current_to, page)
        
        with state_lock:
            worker_status[symbol] = {
                "status": f"Page {page}", 
                "date": current_to.split(' ')[0], 
                "count": len(all_news)
            }

        if not data:
            break

        # Process and track
        for item in data:
            if item.get("url") not in seen_urls:
                seen_urls.add(item["url"])
                all_news.append(item)
        
        dates = [a["publishedDate"] for a in data]
        oldest_on_page = min(dates)

        # 1. Termination Check
        if oldest_on_page.split(' ')[0] <= global_from:
            break

        # 2. Sliding window check
        if page >= 99:
            new_to_date = oldest_on_page.split(' ')[0]
            if new_to_date == last_slid_date:
                dt_obj = datetime.strptime(new_to_date, '%Y-%m-%d')
                new_to_date = (dt_obj - timedelta(days=1)).strftime('%Y-%m-%d')
            
            current_to = new_to_date
            last_slid_date = new_to_date
            page = 0
        else:
            page += 1
            
    if all_news:
        df = pd.DataFrame(all_news)
        df['publishedDate'] = pd.to_datetime(df['publishedDate'])
        df = df.sort_values('publishedDate', ascending=False)
        df.to_parquet(file_path, index=False, engine='pyarrow', compression='snappy')
        with state_lock:
            worker_status[symbol]["status"] = "[green]Finished[/]"
    else:
        with state_lock:
            worker_status[symbol]["status"] = "[yellow]No News[/]"

def make_dashboard(overall_progress):
    """Creates a Group containing the progress bar and the worker table."""
    table = Table(expand=True, box=None)
    table.add_column("Ticker", style="bold cyan", width=12)
    table.add_column("Current Window (To)", style="magenta", width=20)
    table.add_column("Status", style="white", width=15)
    table.add_column("Articles", justify="right", style="bold green", width=12)

    with state_lock:
        # Show only the last active MAX_WORKERS for clarity
        active_items = list(worker_status.items())[-MAX_WORKERS:]
        for sym, info in active_items:
            table.add_row(sym, info["date"], info["status"], f"{info['count']:,}")

    # Combine everything into a display group
    return Group(
        Panel(overall_progress, title="Overall Progress", border_style="blue"),
        Panel(table, title="Active Workers", border_style="white")
    )

def main():
    if not os.path.exists(PROFILES_PATH):
        return
    
    df_profiles = pd.read_csv(PROFILES_PATH)
    symbols = df_profiles[df_profiles['marketCapUSD'] >= MARKET_CAP_THRESHOLD]['symbol'].unique()
    
    # Define the overall progress bar
    overall_progress = Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=None),
        TaskProgressColumn(),
        TimeElapsedColumn(),
    )
    overall_task = overall_progress.add_task(f"Fetching {len(symbols)} tickers...", total=len(symbols))

    with Live(make_dashboard(overall_progress), refresh_per_second=4) as live:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(process_symbol_news, s): s for s in symbols}
            
            for future in as_completed(futures):
                overall_progress.advance(overall_task)
                live.update(make_dashboard(overall_progress))

if __name__ == "__main__":
    main()