# ADR 006: mplfinance for Static Chart Generation

**Date:** 2026-05-12
**Status:** Accepted

## Context
The Vision LLM requires high-contrast, clean candlestick charts to identify VCP patterns and moving average alignments. Interactivity is not required as the output is consumed by an AI, not a human.

## Decision
We will use `mplfinance` (built on Matplotlib) to generate static PNG images. This library is specialized for financial data and provides institutional-grade "style" presets that are easily interpretable by Vision models.

## Consequences
* **Positive:** Lightweight, fast, and generates lossless PNGs. Highly customizable for adding MA lines and volume subplots.
* **Negative:** Not interactive (no zooming/panning), but this is irrelevant for an automated AI-driven pipeline.