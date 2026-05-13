# TQA Documentation & Metadata Review Plan

This plan outlines the necessary updates to the documentation and metadata of the Techno-Quantamental Analyzer (TQA) project to reflect the current state of implementation and recent CLI enhancements.

## 1. Documentation Updates

### `README.md` (Root)
- **CLI Usage**: Update the usage section to reflect the actual [`main.py`](main.py) command structure.
    - Current [`README.md`](README.md) says `uv run main.py --mode batch`.
    - Actual implementation uses `uv run main.py scan` with options like `--limit`, `--min-eps-growth-pct`, `--min-prev-eps`, `--min-latest-eps`, and `--save-prompts`.
- **Features**: Explicitly mention the Trend Template technical filter and the Session Logger.
- **Batching**: Clarify that while native batching is a roadmap item, the current implementation uses parallel asynchronous analysis via OpenRouter.

### `docs/ARCHITECTURE.md`
- **Session Logger**: Ensure the description of `SessionLogger` matches the implementation in [`src/tqa/utils/session_logger.py`](src/tqa/utils/session_logger.py).
- **Technical Filters**: Confirm the "Trend Template" details in the architecture align with the logic in [`src/tqa/screener/universe.py`](src/tqa/screener/universe.py).
- **Data Flow**: Update the data flow description to accurately represent the phased filtering (Fundamentals -> Technicals -> Deep Metrics).

### `docs/ROADMAP.md`
- **Completed Items**: Mark the following as completed (Phase 2):
    - Refactor Screener to include Trend Template and Waterfall filtering.
    - Implement `src/tqa/utils/session_logger.py`.
    - Error handling for rate limits (using `asyncio.Semaphore`).
- **Adjusted Priorities**: Ensure Native Batching and `generate_report.py` remain as high-priority pending items.
- **Future Enhancements**: Review and preserve the existing Phase 3 goals (RS filter, Alpaca integration, etc.) while potentially adding new items discovered during review (e.g., more granular technical indicators).

## 2. Verification of Correctness
- All changes will be verified against the source code:
    - [`main.py`](main.py) for CLI and orchestration.
    - [`src/tqa/screener/universe.py`](src/tqa/screener/universe.py) for filtering logic.
    - [`src/tqa/utils/session_logger.py`](src/tqa/utils/session_logger.py) for logging.

## 3. TODO List Status
- [x] Audit implemented features against README and ROADMAP
- [x] Confirm correctness with existing tests and identify gaps
- [x] Review new CLI functionality in `main.py`
- [ ] Update root `README.md` to reflect actual CLI usage and features
- [ ] Update `docs/ARCHITECTURE.md` to align with current implementation
- [ ] Update `docs/ROADMAP.md` to reflect completed items and revised priorities
- [ ] (Optional) Draft plan for missing features or improvements discovered during review
