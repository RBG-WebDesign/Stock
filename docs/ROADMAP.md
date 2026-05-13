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
* [ ] Connect OpenRouter (synchronous API) to test prompt engineering, base64 payload construction, and Pydantic schema validation.
* [ ] Write `main.py` to orchestrate the pipeline end-to-end for a small test list (e.g., 5 tickers).

## Phase 2: Native Batching & EOD Automation
* [ ] Refactor LLM orchestration to bypass OpenRouter and construct native `.jsonl` batch payloads for direct OpenAI/Anthropic API ingestion (leveraging 50% batch discounts).
* [ ] Implement the batch submission, polling, and retrieval logic within `src/tqa/llm/`.
* [x] Write robust error handling for market data API rate limits (using `asyncio.Semaphore` and exponential backoff) to support 1,000+ concurrent requests.
* [x] Implement automated cache cleanup to prune stale data and manage storage footprint.
* [ ] Implement `generate_report.py` to aggregate the parsed JSON batch results into a sorted Markdown/HTML daily summary.
* [ ] Set up daily execution triggers (e.g., cron job or GitHub Actions) to run automatically at 5:00 PM EST.

## Phase 3: Advanced Signals & Execution (Future)
* [ ] Add Short Interest, Insider Buying, and Institutional Ownership data endpoints from FMP to the deterministic screener.
* [ ] Calculate the anchored VWAP set to after the quarterly earnings release.
* [ ] Build a historical backtesting module utilizing the locally cached, date-suffixed JSON files to analyze screener efficacy over time.
* [ ] Implement automated paper trading via the Alpaca API for setups scoring a 9 or 10 on the LLM confidence scale.