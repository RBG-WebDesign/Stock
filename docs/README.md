# Techno-Quantamental Analyzer (TQA)

An automated, end-of-day (EOD) quantitative and fundamental stock screening pipeline. This tool identifies small-cap breakout candidates by combining strict deterministic financial filters with Large Language Model (LLM) vision and pattern recognition to evaluate chart setups and fundamental narratives.

## 🚀 Overview

The pipeline filters the entire US equity universe down to a highly curated list of momentum small-caps, generates technical charts programmatically, and utilizes LLMs to act as an automated proprietary trader. Relying exclusively on **Financial Modeling Prep (FMP)** for all fundamental and price data, the pipeline constructs asynchronous native batch payloads (via OpenAI or Anthropic) to minimize API costs. It outputs a daily ranked watchlist of actionable swing-trade setups based on CAN SLIM and Minervini methodologies.

## 🧠 Agentic Context (For AI Assistants)

If you are an AI coding assistant (Kilo Code, Copilot, Cursor) working in this repository, **do not begin coding until you have read the documents in the `docs/` folder.** * Start with `docs/README.md` and `docs/ARCHITECTURE.md` to understand the strict module boundaries and file-based caching strategy.

* See `docs/ROADMAP.md` for the current development phase.
* **Jupyter Notebook Preference**: When writing code for prototyping notebooks, avoid encapsulating logic into functions. Keep variables in the global scope to allow for easier inspection and persistence across cells.
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
* **Charting:** `mplfinance`, `pandas`, `matplotlib`
* **Validation:** `pydantic`, `pydantic-settings`
* **AI Provider:** Native OpenAI / Anthropic Batch APIs

## 💻 Installation & Setup

This project uses `uv` for lightning-fast dependency and virtual environment management.

### 1. Prerequisites

Ensure you have `uv` installed:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh

```

### 2. Clone and Sync

```bash
git clone https://github.com/your-org/techno-quantamental-analyzer.git
cd techno-quantamental-analyzer

# Install dependencies and create .venv automatically
uv sync

```

### 3. Environment Configuration

Create a `.env` file in the root directory based on `.env.example`:

```env
FMP_API_KEY=your_fmp_api_key_here
OPENROUTER_API_KEY=your_openrouter_key_for_testing
ANTHROPIC_API_KEY=your_anthropic_api_key_here

```

## 🚀 Usage

The project utilizes `uv run` to ensure scripts run within the locked virtual environment.

### Run the Scanner

Execute the main asynchronous pipeline to fetch data, screen tickers, generate charts, and prepare the LLM batch payload:

```bash
uv run main.py --mode batch

```

### Generate the Report

Once the LLM batch is processed, parse the results and generate the daily sorted watchlist:

```bash
uv run generate_report.py --date 2026-05-12

```

### Automation
The system is configured for nightly automation via cron at 5:00 PM.
The main entry point for automation is [`scripts/nightly_scan.sh`](scripts/nightly_scan.sh).

## 📂 Project Structure

* `config/`: Prompts, Pydantic schemas, and global settings.
* `data/`: Local storage for raw JSON, charts, and batch reports (git-ignored).
* `docs/`: Deep-dive architecture and roadmap documentation.
* `src/tqa/`: Core source code (fetchers, screener, charting, llm).
* `tests/`: Unit and integration test suite.