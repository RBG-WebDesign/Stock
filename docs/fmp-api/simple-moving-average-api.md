# Simple Moving Average API

## About Simple Moving Average API

**Endpoint:**
`https://financialmodelingprep.com/stable/technical-indicators/sma?symbol=AAPL&periodLength=10&timeframe=1day`

---

## Simple Moving Average API Parameters

| Query Parameter | Type | Example |
| --- | --- | --- |
| **symbol*** | string | AAPL |
| **periodLength*** | number | 10 |
| **timeframe*** | string | 1min, 5min, 15min, 30min, 1hour, 4hour, 1day |
| **from** | date | 2026-01-08 |
| **to** | date | 2026-04-08 |

`(*)` **Required**

---

## Response

```json
[
  {
    "date": "2026-04-08 00:00:00",
    "open": 258.45,
    "high": 259.75,
    "low": 256.53,
    "close": 258.9,
    "volume": 39655304,
    "sma": 253.754
  }
]

```