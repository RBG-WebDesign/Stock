# Plan: Implementation of `mplfinance` Charting

This plan details the implementation of automated technical chart generation for the Techno-Quantamental Analyzer (TQA). These charts are designed for consumption by Vision LLMs to identify VCP (Volatility Contraction Property) patterns and moving average setups.

## 1. Objective
Generate high-contrast, static PNG charts for each ticker that survives the deterministic screener. Two charts are required per ticker:
1.  **1-Year Daily Chart**: Focused on intermediate-term momentum and consolidation patterns.
2.  **5-Year Weekly Chart**: Focused on long-term base building and institutional support.

## 2. Technical Specifications

### Chart Components
*   **Price**: Candlestick format.
*   **Volume**: Color-coded bars at the bottom.
*   **Moving Averages (Daily)**: 50-day SMA (Blue), 200-day SMA (Red).
*   **Moving Averages (Weekly)**: 10-week SMA (Blue), 40-week SMA (Red).
*   **Style**: `charles` or `mike` style for high contrast (white background, clear candles).
*   **Dimensions**: Optimized for LLM vision (e.g., 1200x800 or similar).

### Data Requirements
*   Input: `historical` price list from `FMPClient` (already contains ~2 years of data).
*   Processing: Convert JSON to `pandas.DataFrame` with `DatetimeIndex`.

## 3. Implementation Details ([`src/tqa/charting/builder.py`](src/tqa/charting/builder.py))

```python
class ChartBuilder:
    def __init__(self, output_dir: str = "data/charts"):
        self.output_dir = output_dir
        # Ensure directory exists
        
    def _prepare_data(self, historical_data: List[Dict]) -> pd.DataFrame:
        # Convert to DF, sort, set index
        
    def generate_daily_chart(self, ticker: str, df: pd.DataFrame):
        # Slice last 252 days
        # Add 50/200 SMA
        # Save PNG
        
    def generate_weekly_chart(self, ticker: str, df: pd.DataFrame):
        # Resample to weekly ('W-FRI')
        # Add 10/40 SMA
        # Save PNG
```

## 4. Verification Plan
1.  **Mock Data Test**: Use a saved JSON file from `data/raw/historical-price/AAPL_*.json`.
2.  **Visual Inspection**: Manually check the generated PNGs for clarity and correctness of indicators.
3.  **Integration Test**: Run the full pipeline for a single ticker and verify the `data/charts/` directory.

## 5. Roadmap Alignment
This completes Item 12 of Phase 1 in [`docs/ROADMAP.md`](docs/ROADMAP.md).
