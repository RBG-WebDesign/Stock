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
* **Responsibility:** Act as the "Bouncer." Apply deterministic mathematical filters to narrow the universe to high-probability candidates.
* **Waterfall Approach:** To optimize performance and API costs, candidates are filtered in sequential phases:
    1.  **Phase 1: Fundamentals:** Discard stocks without significant YoY EPS or Revenue growth (default > 20%). Uses absolute EPS thresholds to avoid low-base distortions.
    2.  **Phase 2: Technicals:** Apply a strict 7-point "Trend Template" (Price > 50 SMA > 100 SMA > 200 SMA, 52-week range relative strength, and 200 SMA uptrend) to ensure the stock is in a confirmed uptrend.
* **Rule:** No LLM logic or charting logic belongs here. This module only uses data required for initial screening (Income Statements and basic Price History).

### 3. Visualization (`src/tqa/charting/`)
* **Responsibility:** Consume OHLCV DataFrames and output high-contrast PNG images.
* **Rule:** Images are saved locally to `data/charts/`. Charting functions must not make their own API calls; they rely purely on data passed from the orchestrator.

### 4. LLM Orchestration & Batching (`src/tqa/llm/`)
* **Responsibility:** Manage the final analysis pipeline for screening survivors.
* **Timing & Data Flow:** Deep data fetching (Key Metrics, Financial Ratios, News) occurs **after** a ticker passes all screening stages but **before** it is submitted for LLM analysis. This ensures we only pay for "expensive" data and tokens for valid candidates.
* **Process:** Pre-process deep fundamentals into calculated growth metrics (via `src/tqa/utils/data_formatter.py`), base64 encode technical charts, and inject both into `config/prompts.yaml`.
* **Execution:** Currently uses `OpenRouterClient` for parallel asynchronous analysis. Production target (as per ADR 003) is to leverage native provider Batch APIs to minimize costs (50% discount).
* **Rule:** All parsed LLM outputs must be validated against the Pydantic models defined in `config/schemas.py`.

### 5. Logging & Session Management (`src/tqa/utils/session_logger.py`)
* **Responsibility:** Ensure full auditability and "reproducibility" of the agentic pipeline.
* **Mechanism:** Every pipeline run generates a unique session ID (e.g., `YYYYMMDD_HHMMSS`). All LLM inputs (prompts), outputs, configuration settings, and execution logs are saved in a structured format within `data/reports/runs/<session_id>/`.
* **Prompt Debugging:** If the `--save-prompts` flag is used, all raw LLM interactions are appended to `prompts_debug.jsonl` within the session directory.
* **Rule:** No LLM interaction (request or response) should occur without being logged to the active session when auditing is enabled.

## State Management and Caching

We intentionally **do not** use a database (e.g., PostgreSQL/SQLite) in Phase 1 to avoid async write-locks, race conditions, and over-engineering.

* **File-Based Isolation & Nested Caching:** State and cache are managed via flat files in the `data/` directory. To prevent directory bloat, raw API responses are nested into subdirectories based on the provider and specific endpoint (e.g., `data/raw/fmp-key-metrics-api/`, `data/raw/fmp-income-statement/`).
* **Historical Retention (Datetime Suffixing):** To retain a historical log of API responses (useful for future backtesting and preventing data overwrites), all saved JSON files must include an ISO-formatted date suffix. 
  * *Example:* `data/raw/fmp-articles-api/AAPL_2026-05-12.json`
* **Thread Safety:** Because each ticker's endpoint data is written to its own unique file path, this architecture ensures complete thread safety during aggressive `asyncio.gather` execution. 
* **Cache Invalidation:** Before hitting a network endpoint, the system checks for the existence of the file with *today's* date suffix. If `TICKER_YYYY-MM-DD.json` exists for the current trading session, the network call is skipped, and the local file is read instead.
* **Batch Payloads:** Pending LLM jobs are compiled into `.jsonl` files in `data/payloads/` and historical completed reports are dumped into `data/reports/`.