# Techno-Quantamental Analyzer (TQA)

An automated, end-of-day (EOD) quantitative and fundamental stock screening pipeline. This tool identifies breakout candidates by combining strict deterministic financial filters with Large Language Model (LLM) vision and pattern recognition to evaluate chart setups and fundamental narratives.

## 🚀 Overview

The pipeline filters the entire equity universe down to a highly curated list of momentum stocks, generates technical charts programmatically, and utilizes LLMs to act as an automated proprietary trader. Relying exclusively on **Financial Modeling Prep (FMP)** for all fundamental and price data, the pipeline constructs asynchronous native batch payloads (via OpenAI or Anthropic) to minimize API costs. It outputs a daily ranked watchlist of actionable swing-trade setups based on CAN SLIM and Minervini methodologies.

## 🧠 Agentic Context (For AI Assistants)

If you are an AI coding assistant (Cursor, Copilot, Aider) working in this repository, **do not begin coding until you have read the documents in the `docs/` folder.** 

* Start with `docs/README.md` and `docs/ARCHITECTURE.md` to understand the strict module boundaries and file-based caching strategy.
* See `docs/ROADMAP.md` for the current development phase.
* Endpoint documentation for FMP is located in `docs/fmp-api/`.

## ⚙️ Features

* **Deterministic Filtering:** Screens for stocks exhibiting strong fundamentals (EPS/Revenue growth) and positive price momentum (Price > SMAs).
* **Flexible Configuration:** Define complex screening criteria in JSON files, including technical filters (e.g., `price > sma_50`, `sma_50 > sma_100`) and fundamental growth thresholds.
* **Interactive CLI:** Guided interactive menu for launching scans and generating reports without memorizing flags.
* **FMP Exclusive:** Utilizes a single API provider (Financial Modeling Prep) for both institutional-grade fundamental metrics and adjusted OHLCV price data.
* **Automated Asset Generation:** Uses `mplfinance` to programmatically generate clean, lossless PNG charts (1-Year Daily, 5-Year Weekly).
* **Asynchronous Native Batching:** Bypasses synchronous proxy limits by sending JSONL payloads directly to native LLM Batch APIs for significant cost reduction.
* **Structured Output:** Enforces strict Pydantic schemas for LLM responses, ensuring consistent data for reports.

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
FMP_PLAN=premium # Set to premium to enable high-speed bulk data fetches
ANTHROPIC_API_KEY=your_anthropic_key_for_batching
```

## 🚀 Usage

### Interactive Mode
The easiest way to use TQA is to run the interactive menu:
```bash
uv run main.py
```

### Scan Command
Run the end-to-end Quantamental scan using a configuration file:
```bash
# Scan using a pre-defined strategy
uv run main.py scan --config can_slim.json

# Scan with CLI overrides
uv run main.py scan --config can_slim.json --limit 100 --min-eps-growth-pct 25.0
```

### Report Command
Generate a PDF report from a completed session:
```bash
# Interactive report generation (lists recent sessions)
uv run main.py report

# Generate report for a specific session
uv run main.py report <session_id>
```

### CLI Options for `scan`
* `--config`, `-c`: Path to a JSON configuration file.

## 🤖 Automation

TQA includes a nightly automation script to run multiple scanning configurations sequentially.

### Nightly Scans
The script [`scripts/nightly_scan.sh`](scripts/nightly_scan.sh) is configured to run every day at 5:00 PM via cron. It executes scans for:
- Master Analyst (USA & China)
- Institutional Accumulator (USA & China)
- CAN SLIM (USA & China)

Logs for these automated runs are stored in [`logs/cron_scans.log`](logs/cron_scans.log).

To manually trigger the nightly suite:
```bash
./scripts/nightly_scan.sh
```
* `--limit`, `-l`: Max tickers to fetch from the FMP universe.
* `--min-eps-growth-pct`, `-e`: Minimum YoY EPS growth % threshold.
* `--min-market-cap`: Minimum market capitalization in Millions.
* `--save-prompts`, `-s`: Save all LLM prompts and responses for auditing.

## 📄 Configuration Files

TQA supports granular control via JSON configuration files. Key sections include:

- **`pipeline`**: Global settings like `model`, `universe_limit`, and `prompt_mode`.
- **`market_cap`**: `min_m` and `max_m` (in millions).
- **`fundamental_filters`**: Growth thresholds and acceleration requirements.
- **`technical_filters`**: A list of string expressions (e.g., `"price > sma_200"`, `"sma_50 > sma_200"`).

### Sample Configs
- `can_slim.json`: Classic CAN SLIM criteria.
- `master_analyst_usa.json`: Comprehensive US market analysis.
- `can_slim_china.json`: Strategy adapted for China/HK markets.
- `institutional_accumulator_usa.json`: Focus on high-volume institutional footprints.
- `master_analyst_china.json`: Comprehensive analysis for China/HK markets.

## 🧪 Testing

This project uses `pytest`. To run the tests, ensure you are in the root directory and set the `PYTHONPATH`:

```bash
PYTHONPATH=. uv run pytest
```
