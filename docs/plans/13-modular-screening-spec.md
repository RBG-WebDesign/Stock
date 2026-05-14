# Modular Screening & Configuration Spec

The Techno-Quantamental Analyzer (TQA) supports dynamic configuration via JSON files. This allows users to define custom strategies without modifying the source code.

## Configuration File (`config.json`)

The configuration file allows you to override default pipeline settings, fundamental filters, and technical setup conditions.

### Example Schema

```json
{
  "pipeline": {
    "universe_limit": 50,
    "model": "google/gemini-3-flash-preview",
    "prompt_mode": "master_analyst",
    "save_prompts": false,
    "news_summary_max_chars": 500,
    "max_recent_articles": 10
  },
  "market_cap": {
    "min_m": 100,
    "max_m": 1000
  },
  "fundamental_filters": {
    "min_eps_growth": 20.0,
    "min_rev_growth": 20.0,
    "max_rev_growth": null,
    "min_prev_eps": null,
    "max_prev_eps": null,
    "min_latest_eps": null,
    "require_acceleration": false
  },
  "technical_filters": [
    "price > sma_200",
    "sma_50 > sma_200",
    "sma_200 > sma_200_22d",
    "price > sma_50",
    "price >= 1.30 * low_52w",
    "price >= 0.75 * high_52w"
  ]
}
```

## Technical Indicators

The following indicators are automatically calculated and available for use in the `technical_filters` list:

| Indicator | Description |
|-----------|-------------|
| `price` | The current closing price. |
| `open`, `high`, `low`, `close`, `volume` | Standard OHLCV data. |
| `sma_10`, `sma_20`, `sma_50`, `sma_100`, `sma_200` | Simple Moving Averages. |
| `sma_X_22d` | The value of the SMA `X` from 22 trading days ago (approx. 1 month). |
| `low_52w` | The 52-week (252 trading days) low. |
| `high_52w` | The 52-week (252 trading days) high. |
| `vol_avg_20` | The 20-day average trading volume. |

## Filter Logic

Filters use `pandas.eval()` syntax. You can use standard comparison operators (`>`, `<`, `>=`, `<=`, `==`) and logical operators (though currently, each string in the list is treated as a separate condition that must be `True`).

Example of a custom bearish/short condition:
```json
"technical_filters": [
  "price < sma_200",
  "sma_50 < sma_200",
  "price < sma_20"
]
```
