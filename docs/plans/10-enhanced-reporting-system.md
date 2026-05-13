# Plan: Enhanced Quantamental Reporting

This plan outlines the implementation of an aesthetic, informative PDF reporting system for the TQA pipeline.

## 1. Core Objectives
- **Aesthetic PDF Generation**: Create high-quality reports with a dashboard-style executive summary and detailed stock deep dives.
- **Interactive CLI**: Update `main.py report` to be interactive, allowing users to select sessions, models, and confidence thresholds.
- **Data Enrichment**: Ensure the report captures the entire filtering waterfall (Universe -> Fundamentals -> Technicals -> Final Watchlist).
- **LLM Synthesis**: Display structured LLM outputs alongside daily and weekly charts.

## 2. Technical Architecture

### PDF Generation
- **Library**: `FPDF2` for lightweight, programmatic PDF creation, or `Markdown2` + `WeasyPrint` for HTML-to-PDF flexibility.
- **Dashboard Infographic (The "Funnel Metrics"):**
    - **Universe Depth**: Total stocks scanned vs. total stocks in the target market cap (e.g., "1100 / 3500 Scanned").
    - **Fundamental Attrition**: Count and % of stocks discarded for low EPS/Rev growth (e.g., "400 Passed, 700 Filtered").
    - **Technical Precision**: Count of stocks passing the 7-point Trend Template (e.g., "200 Passed, 200 Filtered").
    - **Watchlist Conversion**: Final number of stocks analyzed by LLM and how many met the confidence threshold (e.g., "15 Watchlist Stocks, 5 High Conviction").
    - **Settings Snapshot**: A visual box showing: `Min EPS Growth`, `Min Prev EPS`, `Trend Template Active`, `Market Cap Range`.

### CLI Enhancements (`main.py`)
- **Interactive Selection**: Use `rich.prompt` to let the user:
    - Select from the last 5 sessions (default to most recent).
    - Choose a "Prompt Mode" (Master Analyst, CAN SLIM, etc.).
    - Set a `min_confidence` score (e.g., 8/10).
- **Arguments**: Add `--model`, `--min-confidence`, and `--interactive` flags to the `report` command.

### Data Model
- **Source**: `data/reports/runs/<session_id>/`
    - `run_config.json`: For filter criteria and settings.
    - `pipeline.log`: To parse the number of stocks passing each phase.
    - `prompts_debug.jsonl`: For LLM analysis results.
    - `data/charts/`: For PNG chart inclusion.

## 3. Report Structure
1.  **Header**: Session ID, Date, Selected Model, Prompt Mode.
2.  **Executive Summary**:
    - Funnel Dashboard (Infographic style).
    - Market Overview (optional aggregate metrics).
3.  **Watchlist**: High-confidence stocks (sorted by score).
4.  **Deep Dives (per ticker)**:
    - Fundamental Summary (EPS/Rev growth).
    - Technical Analysis (SMA status, Pivot Point).
    - LLM Verdict (Catalyst, VCP status).
    - **Visuals**: 1-Year Daily and 5-Year Weekly charts side-by-side.

## 4. Todo List
- [ ] Research `FPDF2` or `WeasyPrint` for layout flexibility.
- [ ] Create `src/tqa/utils/report_builder.py` with `PDFGenerator` class.
- [ ] Refactor `main.py` `report` command for interactivity.
- [ ] Update `SessionLogger` to record funnel stats (e.g., counts at each phase) in `run_config.json`.
- [ ] Design the PDF template (fonts, colors, layout).
- [ ] Implement image embedding logic for charts.
- [ ] Verify handling of various prompt modes in the final report.

## 5. Verification Plan
- Generate a report for a session with multiple survivors and verify the "Funnel" counts match the logs.
- Test the interactive CLI by choosing different sessions and confidence scores.
- Inspect the PDF for layout correctness (especially side-by-side charts).
