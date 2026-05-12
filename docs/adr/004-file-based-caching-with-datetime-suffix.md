# ADR 004: File-Based Caching with Datetime Suffix

**Date:** 2026-05-12
**Status:** Accepted

## Context
The system performs high-concurrency async I/O. We need a way to cache API responses to save money and stay within rate limits. A centralized database (SQLite) introduces complexities regarding async write-locks and race conditions when multiple tickers try to update the DB at once.

## Decision
We will use a flat-file caching system. Responses will be stored in `data/raw/<endpoint-name>/<TICKER>_<YYYY-MM-DD>.json`. 

## Consequences
* **Positive:** No race conditions (each file is unique to a ticker/date). Easy to debug by simply opening a JSON file. Provides a historical "time machine" of data for future backtesting.
* **Negative:** Directory bloat over time. Requires a manual or automated cleanup script to delete files older than X days if storage becomes an issue.