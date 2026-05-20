# Plan: Adapt Stock Downloader for 30-Minute Interval Data

This plan outlines the steps to create a new script `1-download-stock-30min.py` based on the existing `1-download-stock-daily.py`, adapted to fetch intraday 30-minute bar data from Financial Modeling Prep (FMP).

## 1. Script Creation
- Create `notebooks/fmp-full-download/1-download-stock-30min.py`.
- Copy the core logic from `1-download-stock-daily.py`.

## 2. Configuration Updates
- **Output Directory**: Change `OUTPUT_DIR` from `data/prices` to `data/prices-30min` to avoid conflicts with daily data.
- **Date Chunks**: Update `DATE_CHUNKS`. Intraday data is significantly more voluminous than daily data. 
    - Suggest starting from `2018-01-01` to `2026-05-15`.
    - Split into smaller chunks (e.g., 2-year intervals) to prevent timeouts or excessively large payloads if the API has response size limits.
    - Example Chunks:
        - `("2018-01-01", "2019-12-31")`
        - `("2020-01-01", "2021-12-31")`
        - `("2022-01-01", "2023-12-31")`
        - `("2024-01-01", "2026-05-15")`

## 3. API Integration
- **Endpoint**: Update the `url` in `fetch_prices_with_backoff` to:
  `https://financialmodelingprep.com/stable/historical-chart/30min`
- **Parameters**: Keep `symbol`, `from`, `to`, and `apikey`. The endpoint supports these as query parameters according to the documentation.

## 4. Data Processing
- **Response Format**: The `historical-chart/30min` endpoint returns a flat list of dictionaries:
  ```json
  [{"date": "2025-02-04 15:30:00", "open": 232.29, ...}, ...]
  ```
- **DataFrame Conversion**: `pd.DataFrame(data)` will correctly parse this list.
- **Deduplication**: Keep the logic `drop_duplicates(subset=['date'])`. Note that the `date` column will now include timestamps.
- **Storage**: Save to `.parquet` using the same directory partitioning logic (by first character of the symbol).

## 5. Verification
- Verify that the script correctly loads symbols from the specified CSV.
- Ensure `MARKET_CAP_THRESHOLD` and `MAX_WORKERS` are appropriately set for the user's needs.

## Mermaid Workflow

```mermaid
graph TD
    A[Start] --> B[Load Symbols from CSV]
    B --> C[Filter by Market Cap >= 1B]
    C --> D[Initialize ThreadPoolExecutor]
    D --> E[Process Symbol in Parallel]
    E --> F{File Exists?}
    F -- Yes --> G[Skip Symbol]
    F -- No --> H[Loop Through DATE_CHUNKS]
    H --> I[Fetch 30min Data from FMP]
    I --> J[Collect Chunks]
    J --> K[Concatenate & Deduplicate by 'date']
    K --> L[Save to data/prices-30min/{initial}/{symbol}.parquet]
    L --> M[Finish Symbol]
    M --> N[End]
```
