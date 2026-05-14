# Technical Specification: Bulk Data Optimization Fixes

## 1. Problem Statement
The recent bulk data optimization introduced several logic gaps:
- **Inconsistent formatting**: CSV data (from bulk API) uses different key naming conventions (likely snake_case) compared to JSON data (camelCase), causing individual fetcher fallbacks to fail or return inconsistent data.
- **Proactive caching issues**: Manual caching of individual records from bulk data is error-prone and doesn't handle list/dict wrapping correctly for downstream consumers.
- **Logic Gaps in `main.py`**: Inconsistent variable naming and potential issues with merging auxiliary data (consensus, ratings) into the final watchlist objects.
- **Cache Key Inconsistency**: The `_CSV` suffix is handled manually and inconsistently across different bulk methods.

## 2. Proposed Changes

### 2.1 Normalization Layer (`src/tqa/data_fetchers/base.py`)
Add a normalization step to `_make_request` that ensures all data returned from CSV sources matches the camelCase format of JSON sources.

```python
def _normalize_keys(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Converts snake_case keys to camelCase for consistency with FMP JSON API."""
    def to_camel(snake_str):
        components = snake_str.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])

    normalized = []
    for item in data:
        normalized.append({to_camel(k): v for k, v in item.items()})
    return normalized
```

### 2.2 Standardized Proactive Caching (`src/tqa/data_fetchers/fmp.py`)
Implement a helper method to handle the complexities of proactive caching.

```python
def _proactive_cache_individual(self, endpoint: str, ticker: str, data: Any):
    """
    Saves a piece of data into the local cache as if it were fetched individually.
    Ensures format compatibility (e.g. wrapping statements in a list).
    """
    cache_path = self._get_cache_path(endpoint, ticker)
    if cache_path.exists():
        return
        
    # Wrap in list if it's an endpoint that usually returns a list (e.g. statements)
    list_endpoints = ["income-statement", "key-metrics", "ratios", "earnings"]
    if endpoint in list_endpoints and not isinstance(data, list):
        data = [data]
        
    with open(cache_path, "w") as f:
        json.dump(data, f, indent=4)
```

### 2.3 Phase 3 Logic Cleanup (`main.py`)
- Standardize on `ticker` variable.
- Use `.copy()` when merging bulk records to prevent side effects.
- Ensure `profile` is properly initialized if both individual and bulk fetches fail.

### 2.4 Data Enrichment (`src/tqa/utils/data_formatter.py`)
Update `format_fundamentals_for_llm` to extract `analyst_consensus` and `bulk_rating` from the `profile` object so the LLM can use this information.

## 3. Implementation Plan

1.  **BaseDataFetcher**: Add `_normalize_keys` and update `_make_request` to use it when `datatype=csv`.
2.  **FMPClient**: 
    - Add `_proactive_cache_individual`.
    - Update `fetch_income_statement_bulk` to use the helper.
    - Standardize all `ticker_key` generation to include `_CSV` via a common pattern.
3.  **Main Pipeline**: 
    - Refactor `fetch_deep` to use consistent naming and robust merging.
    - Ensure all auxiliary bulk data is correctly attached to the `ticker_data` passed to the orchestrator.
4.  **LLM Context**: Update the formatter to include the new data points in the LLM payload.

## 4. Verification
- Run a scan with `FMP_PLAN=premium` and verify that individual cache files are created in the correct format.
- Check `prompts_debug.jsonl` to ensure `analyst_consensus` and `bulk_rating` are present in the `profile` node.
- Verify that the report generates correctly with the enriched data.
