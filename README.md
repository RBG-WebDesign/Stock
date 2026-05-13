# Techno-Quantamental Analyzer (TQA)

An automated, end-of-day (EOD) quantitative and fundamental stock screening pipeline. This tool identifies small-cap breakout candidates by combining strict deterministic financial filters with Large Language Model (LLM) vision and pattern recognition to evaluate chart setups and fundamental narratives.

## 🚀 Overview

The pipeline filters the entire US equity universe down to a highly curated list of momentum small-caps, generates technical charts programmatically, and utilizes LLMs to act as an automated proprietary trader. Relying exclusively on **Financial Modeling Prep (FMP)** for all fundamental and price data, the pipeline constructs asynchronous native batch payloads (via OpenAI or Anthropic) to minimize API costs. It outputs a daily ranked watchlist of actionable swing-trade setups based on CAN SLIM and Minervini methodologies.

## 🧠 Agentic Context (For AI Assistants)

If you are an AI coding assistant (Cursor, Copilot, Aider) working in this repository, **do not begin coding until you have read the documents in the `docs/` folder.** * Start with `docs/README.md` and `docs/ARCHITECTURE.md` to understand the strict module boundaries and file-based caching strategy.

* See `docs/ROADMAP.md` for the current development phase.
* Endpoint documentation for FMP is located in `docs/fmp-api/`.

## ⚙️ Features

* **Deterministic Filtering:** Screens for $100M - $1B market cap stocks exhibiting strong fundamentals (EPS growth > 20% over consecutive quarters) and positive price momentum (1-month performance > 0%, Price > 50 SMA).
* **FMP Exclusive:** Utilizes a single API provider (Financial Modeling Prep) for both institutional-grade fundamental metrics and adjusted OHLCV price data.
* **Automated Asset Generation:** Uses `mplfinance` to programmatically generate clean, lossless PNG charts (1-Year Daily, 5-Year Weekly) isolated from network I/O.
* **Asynchronous Native Batching:** Bypasses synchronous proxy limits by compiling JSONL payloads and sending them directly to native LLM Batch APIs (e.g., Anthropic/OpenAI) for a 50% cost reduction.
* **Structured Output:** Enforces strict Pydantic schemas, returning actionable JSON data including confidence scores, pivot points, and invalidation levels.

## 🛠️ Tech Stack

* **Language:** Python 3.11+
* **Package Manager:** `uv`
* **Market Data API:** Financial Modeling Prep (FMP)
* **Charting:** `mplfinance` / `pandas`
* **AI Provider:** Native OpenAI / Anthropic Batch APIs (with OpenRouter fallback for sync testing)

## 💻 Installation

This project uses `uv` for lightning-fast dependency and virtual environment management.

1. Clone the repository:
```bash
git clone https://github.com/your-org/techno-quantamental-analyzer.git
cd techno-quantamental-analyzer

```


2. Install `uv` (if you don't have it installed globally):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh

```


3. Sync the project (this automatically creates the `.venv` and installs all locked dependencies):
```bash
uv sync

```


4. Activate the virtual environment:
```bash
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`

```


5. Configure Environment Variables:
Create a `.env` file in the root directory and add your API keys:
```env
FMP_API_KEY=your_fmp_api_key_here
OPENROUTER_API_KEY=your_openrouter_key_for_testing
ANTHROPIC_API_KEY=your_anthropic_key_for_batching

```



## 🚀 Usage

Run the main asynchronous pipeline after market close to generate the batch payload:

```bash
uv run main.py --mode batch

```

To parse the returned batch file and generate the sorted daily markdown report:

```bash
uv run generate_report.py --date YYYY-MM-DD

```

## 🧪 Testing

This project uses `pytest`. To run the tests, ensure you are in the root directory and set the `PYTHONPATH`:

```bash
PYTHONPATH=. uv run pytest
```

Alternatively, you can run specific tests:

```bash
PYTHONPATH=. uv run pytest tests/test_orchestrator.py
```