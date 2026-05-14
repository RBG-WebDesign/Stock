# Plan: Enhanced Reporting and Clarification

This plan addresses the missing company profile in PDF reports and clarifies the Risk/Reward calculations and breakout trading terminology.

## Problem Analysis
1. **Missing Profile**: Data is fetched but not logged in `prompts_debug.jsonl`, which `report_builder.py` uses as its data source.
2. **R/R Confusion**: The report calculates reward as a fixed 20% gain from the "Entry Pivot". This isn't explicit, leading to confusion when "Entry Pivot" is higher than the current price.
3. **Terminology**: Users may not be familiar with "Entry Pivot" as the breakout point.

## Proposed Changes

### 1. Data Persistence (Session Logging)
- **File**: `src/tqa/utils/session_logger.py`
  - Modify `log_prompt` to accept an optional `profile: Dict`.
  - Include the `profile` in the JSON entry written to `prompts_debug.jsonl`.
- **File**: `src/tqa/llm/orchestrator.py`
  - Pass `ticker_data.get("profile")` when calling `session.log_prompt`.

### 2. PDF Report Enhancement
- **File**: `src/tqa/utils/report_builder.py`
  - **Company Overview**: Enhance with Market Cap, Beta, and Vol Avg from the profile.
  - **Metric Boxes**:
    - Add a new box: **"Target Price (20%)"**.
    - Rename **"Est. Risk/Reward"** to **"R/R (at 20% Target)"**.
  - **Terminology Legend**: Add a small section at the bottom of the stock page or in the footer explaining:
    - **Entry Pivot**: The price level to watch for a breakout entry.
    - **Stop Loss**: The price level where the technical setup is considered invalidated.
    - **Target Price**: A standard 20% profit goal used for risk/reward estimation.

### 3. Logic Refinement
- Ensure the R/R calculation in `report_builder.py` remains consistent but is more transparently labeled.

## Verification Plan
1. Run a sample scan with `-s` (save prompts) and a small universe.
2. Check `data/reports/runs/<session_id>/prompts_debug.jsonl` for the `profile` key.
3. Generate the report and verify:
   - Company Overview is present and populated.
   - Target Price box is visible.
   - R/R label is updated.
   - Legend/Notes are present.
