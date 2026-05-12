# Techno-Quantamental Analyzer

An automated, end-of-day (EOD) quantitative and fundamental stock screening pipeline. This tool identifies small-cap breakout candidates by combining strict deterministic financial filters with Large Language Model (LLM) vision and pattern recognition to evaluate chart setups and fundamental narratives.

## 🚀 Overview

The pipeline filters the entire US equity universe down to a highly curated list of momentum small-caps, generates technical charts programmatically, and utilizes LLMs to act as an automated proprietary trader. By routing through OpenRouter, the pipeline allows for seamless swapping of the underlying vision and reasoning models to optimize for cost and performance. It outputs a daily ranked watchlist of actionable swing-trade setups based on CAN SLIM and Minervini methodologies.

## ⚙️ Features

* **Deterministic Filtering:** Screens for $100M - $1B market cap stocks exhibiting strong fundamentals (EPS growth > 20% over consecutive quarters) and positive price momentum (1-month performance > 0%, Price > 50 SMA).
* **Automated Asset Generation:** Uses `mplfinance` (or `Plotly`) to programmatically generate clean, lossless PNG charts (1-Year Daily OHLCV, 5-Year Weekly OHLCV) without relying on walled-garden web apps.
* **Model Agnosticism via OpenRouter:** Easily swap between the best vision models (e.g., GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro) with a single configuration change.
* **Structured Output:** Enforces strict JSON schemas from the LLM, returning actionable data including confidence scores, pivot points, and invalidation levels.

## 🛠️ Tech Stack

* **Language:** Python 3.10+
* **Package Manager:** `uv`
* **Market Data API:** Financial Modeling Prep (FMP) / Polygon.io
* **Charting:** `mplfinance` / `pandas`
* **AI Provider:** OpenRouter (OpenAI, Anthropic, Google, etc.)

## 🏗️ Pipeline Architecture

1. **Universe Definition:** Fetches the total US equities list and filters for target market cap ($100M–$1B).
2. **The "Bouncer" (Screening):** Applies hard mathematical filters (EPS, moving averages, recent performance) to reduce thousands of tickers down to ~20-50 high-quality candidates.
3. **Asset Generation:** Downloads historical OHLCV data for the curated list and renders high-contrast PNG charts.
4. **Payload Construction:** Base64 encodes the PNGs and pairs them with fundamental context (current price, SMA values, EPS stats) into JSON payloads.
5. **LLM Evaluation:** Submits the payloads to the chosen model via OpenRouter. The model analyzes the charts for Volatility Contraction Patterns (VCP), supply/demand zones, and fundamental alignment.
6. **Parsing & Reporting:** Retrieves the processed responses, sorts the resulting JSON objects by `confidence_score`, and generates the daily watchlist.

## 💻 Installation

1. Clone the repository:
```bash
git clone https://github.com/your-org/techno-quantamental-analyzer.git
cd techno-quantamental-analyzer

```


2. Create and activate a virtual environment using `uv`:
```bash
# Install uv if you haven't already: curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`

```


3. Install dependencies:
```bash
uv pip install -r requirements.txt

```


4. Configure Environment Variables:
Create a `.env` file in the root directory and add your API keys:
```env
MARKET_DATA_API_KEY=your_fmp_or_polygon_key_here
OPENROUTER_API_KEY=your_openrouter_key_here
DEFAULT_MODEL=anthropic/claude-3.5-sonnet  # Or your preferred model tag

```



## 🚀 Usage

Run the main pipeline after market close:

```bash
python main.py --mode scan

```

To parse the generated outputs and generate the sorted daily report:

```bash
python generate_report.py --date YYYY-MM-DD

```

## 📄 Example LLM Output Schema

The LLM is prompted to return data in the following strictly enforced JSON structure:

```json
{
  "ticker": "XYZ",
  "primary_pattern": "Cup and Handle",
  "fundamental_catalyst": "Consecutive quarters of >25% EPS growth and expanding gross margins.",
  "suggested_entry_pivot": 45.50,
  "suggested_stop_loss": 42.10,
  "confidence_score": 8,
  "bull_case": "Price consolidating tightly near the 50 SMA on declining volume, indicating institutional accumulation.",
  "bear_case_risks": "Overall sector relative strength is lagging the S&P 500; macro environment could pull the stock below the 200 SMA."
}

```