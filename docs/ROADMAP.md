# Development Roadmap

## Phase 1: Minimum Viable Pipeline (Current)
* [x] Define project architecture, nested directory structure, and initialize `uv` environment.
* [x] Draft foundational documentation (`ARCHITECTURE.md`, ADRs, `prompts.yaml`, Pydantic schemas).
* [x] Implement async `BaseDataFetcher` class to establish the contract for all external API clients.
* [x] Implement `FMPClient` for fetching the $100M-$1B universe and fundamental metrics.
* [x] Build the local caching utility to read/write JSON files mapped to `data/raw/<endpoint>/TICKER_YYYY-MM-DD.json`.
* [x] Build the `screener` module to apply deterministic mathematical filters (e.g., turnaround-aware EPS growth).
* [x] Implement robust logging with correct path resolution across different execution contexts.
* [x] Establish verified integration tests for core components (`tests/test_data_fetchers.py`).
* [x] Implement `mplfinance` charting for 1-Year Daily and 5-Year Weekly timeframes, saving PNGs to `data/charts/`.
* [x] Connect OpenRouter (async via `aiohttp`) to test prompt engineering, base64 payload construction, and Pydantic schema validation.
* [x] Write `main.py` to orchestrate the pipeline end-to-end for a small test list (e.g., 5 tickers).

## Phase 2: EOD Automation & Refinement (In Progress)
* [x] Refactor Screener to include 7-point Trend Template and Waterfall filtering.
* [-] Implement `src/tqa/utils/session_logger.py` for structured session tracking and prompt auditing (Funnel metrics in progress).
* [x] Implement robust error handling for market data API rate limits (using `asyncio.Semaphore` and exponential backoff).
* [x] Implement automated cache cleanup to prune stale data.
* [-] Implement native `.jsonl` batch payloads for OpenAI/Anthropic (currently uses parallel sync calls via OpenRouter).
* [ ] Implement the batch submission, polling, and retrieval logic within `src/tqa/llm/`.
* [ ] Implement `generate_report.py` (or `main.py report`) to aggregate results into a sorted Markdown summary.
* [ ] Set up daily execution triggers (e.g., cron job or GitHub Actions) to run automatically at 5:00 PM EST.

## Phase 3: Advanced Signals & Execution (Future)
* [ ] Implement Relative Strength (RS) filter comparing ticker performance against S&P 500 (SPY).
* [ ] Add Short Interest, Insider Buying, and Institutional Ownership data endpoints from FMP to the deterministic screener.
* [ ] Calculate the anchored VWAP set to after the quarterly earnings release.
* [ ] Build a historical backtesting module utilizing the locally cached, date-suffixed JSON files to analyze screener efficacy over time.
* [ ] Implement automated paper trading via the Alpaca API for setups scoring a 9 or 10 on the LLM confidence scale.