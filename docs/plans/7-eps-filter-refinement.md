# Plan: EPS Filter Refinement

The goal is to improve the EPS filtering logic to avoid misleading growth percentages caused by near-zero bases and to provide more granular control over absolute EPS values.

## Problem Statement
1.  **Near-Zero Base**: If the previous quarter's EPS was very small (e.g., 0.001), a small increase in absolute EPS (e.g., to 0.05) results in an extremely high growth percentage (4900%), which can be misleading for trend analysis.
2.  **Ambiguous CLI Arguments**: The current `--eps` flag is used for growth percentage, but users may confuse it with absolute EPS values.
3.  **Negative Base Handling**: Confirmation of how growth is calculated when the previous EPS was negative.

## Proposed Changes

### 1. `src/tqa/screener/universe.py`
-   Modify `Screener.__init__` to include:
    -   `min_prev_eps: Optional[float] = None`
    -   `min_latest_eps: Optional[float] = None`
-   Update `check_fundamentals` to:
    -   Filter out tickers if `prev_eps < min_prev_eps` (if provided).
    -   Filter out tickers if `latest_eps < min_latest_eps` (if provided).
-   The growth calculation remains `((latest - prev) / abs(prev)) * 100` to correctly handle negative-to-positive transitions.

### 2. `main.py`
-   Update the `scan` command to add:
    -   `--min-prev-eps`: Minimum absolute EPS for the previous quarter.
    -   `--min-latest-eps`: Minimum absolute EPS for the most recent quarter.
-   Rename `--eps` to `--min-eps-growth-pct` to be more explicit about its meaning.
-   Pass these new parameters through `run_pipeline` to the `Screener`.

## Verification Plan
1.  **Manual Test**: Run `python main.py scan --eps 20 --min-prev-eps 0.01` and verify that tickers with very small previous EPS are excluded.
2.  **Code Review**: Ensure that the `abs(prev)` logic for growth calculation is clearly documented or understood as the standard approach for negative bases.

## User Questions Answered
-   **EPS Growth Calculation for Negative Base**: Currently calculated as `((latest - prev) / abs(prev)) * 100`. For `-0.1 to 0.05`, this results in `150%` growth.
-   **Meaning of `--eps 0`**: It currently means "Minimum 0% EPS Growth". It is **not** the absolute EPS of the recent quarter.
