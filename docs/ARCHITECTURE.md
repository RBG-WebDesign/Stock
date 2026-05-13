# System Architecture

## Core Philosophy
The Techno-Quantamental Analyzer (TQA) is an automated, end-of-day (EOD) swing trading screener. It operates on a "Quantamental" philosophy: 
1. **Quantitative/Deterministic:** Use strict math and fundamental metrics to ruthlessly filter noise.
2. **Qualitative/Agentic:** Use Vision LLMs to synthesize chart patterns (Technical Analysis) and fundamental narratives.

## Concurrency & Performance Strategy
The pipeline processes between 1,000 and 2,000 small-cap equities. Performance is achieved through heavily concurrent I/O operations.
* **Network I/O:** Market data fetching is handled asynchronously via `asyncio` and `aiohttp`.
* **Rate Limiting:** Concurrency is bottlenecked strictly by API rate limits using `asyncio.Semaphore` to prevent 429 HTTP errors from FMP.
* **Computation:** CPU-bound tasks (like `mplfinance` chart generation) are isolated from the network event loop to prevent blocking.

## System Boundaries & Data Flow

The system is strictly modular. An AI agent modifying this codebase must respect these boundaries:

### 1. Data Fetching (`src/tqa/data_fetchers/`)
* **Responsibility:** Ingest raw market data (OHLCV) and comprehensive fundamental metrics (Income Statements, Institutional Ownership, Earnings Surprises, Analyst Estimates) concurrently.
* **Rule:** All external API clients must inherit from `base.py`. No data transformation happens here; just fetching and standardizing the output into raw dictionaries or DataFrames.
* **Execution:** Must support async methods (e.g., `async def fetch_ticker_data()`).

### 2. Screening & Math (`src/tqa/screener/`)
* **Responsibility:** Act as the "Bouncer." Apply deterministic filters (e.g., EPS > 20%, Price > 50 SMA).
* **Rule:** No LLM logic or charting logic belongs here. This module outputs a clean list of `ticker` strings that survived the filter.

### 3. Visualization (`src/tqa/charting/`)
* **Responsibility:** Consume OHLCV DataFrames and output high-contrast PNG images.
* **Rule:** Images are saved locally to `data/charts/`. Charting functions must not make their own API calls; they rely purely on data passed from the orchestrator.

### 4. LLM Orchestration & Batching (`src/tqa/llm/`)
* **Responsibility:** Pre-process raw fundamentals into calculated growth metrics (via `src/tqa/utils/data_formatter.py`), base64 encode charts, and inject both into `config/prompts.yaml`.
* **Provider Integration:** We bypass OpenRouter for this stage and communicate directly with native provider Batch APIs (e.g., OpenAI or Anthropic) to leverage 50% batch token discounts. 
* **Rule:** All parsed LLM outputs must be validated against the Pydantic models defined in `config/schemas.py` immediately upon receipt from the completed batch file.

## State Management and Caching

We intentionally **do not** use a database (e.g., PostgreSQL/SQLite) in Phase 1 to avoid async write-locks, race conditions, and over-engineering.

* **File-Based Isolation & Nested Caching:** State and cache are managed via flat files in the `data/` directory. To prevent directory bloat, raw API responses are nested into subdirectories based on the provider and specific endpoint (e.g., `data/raw/fmp-key-metrics-api/`, `data/raw/fmp-income-statement/`).
* **Historical Retention (Datetime Suffixing):** To retain a historical log of API responses (useful for future backtesting and preventing data overwrites), all saved JSON files must include an ISO-formatted date suffix. 
  * *Example:* `data/raw/fmp-articles-api/AAPL_2026-05-12.json`
* **Thread Safety:** Because each ticker's endpoint data is written to its own unique file path, this architecture ensures complete thread safety during aggressive `asyncio.gather` execution. 
* **Cache Invalidation:** Before hitting a network endpoint, the system checks for the existence of the file with *today's* date suffix. If `TICKER_YYYY-MM-DD.json` exists for the current trading session, the network call is skipped, and the local file is read instead.
* **Batch Payloads:** Pending LLM jobs are compiled into `.jsonl` files in `data/payloads/` and historical completed reports are dumped into `data/reports/`.