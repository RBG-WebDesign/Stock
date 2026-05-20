# 5-Minute Interval Stock Chart API

The **Financial Modeling Prep (FMP)** 5-Minute Interval Stock Chart API provides granular, high-frequency intraday data. It is specifically built for active traders and scalpers who require precise timing to identify short-term price momentum and execution points.

---

### Key Features

* **Short-Term Price Analysis:** Monitor price action in tight 5-minute windows, ideal for capturing rapid market shifts.
* **Precise Trading Data:** Includes Open, High, Low, Close (OHLC), and volume, allowing for the identification of micro-patterns like "bull flags" or "head and shoulders" within the trading day.
* **High-Resolution Charting:** Provides the necessary data density to build professional-grade intraday charts.
* **Historical Access:** Retrieve past 5-minute data to perform detailed post-trade analysis or backtest high-frequency trading algorithms.
* **Optimized for Active Traders:** Delivers fast, reliable updates for those making multiple trades per session.

---

### API Reference

**Endpoint URL**
`https://financialmodelingprep.com/stable/historical-chart/5min?symbol=AAPL`

#### Query Parameters

| Parameter | Type | Required | Example | Description |
| --- | --- | --- | --- | --- |
| **symbol** | string | Yes | `AAPL` | The ticker symbol of the stock. |
| **from** | date | No | `2024-01-01` | The start date for the data range. |
| **to** | date | No | `2024-03-01` | The end date for the data range. |
| **nonadjusted** | boolean | No | `false` | Whether to return non-adjusted data. |

---

> **Example Use Case**
> A day trader monitors **Apple (AAPL)** using 5-minute intervals to spot sudden spikes in volume. By seeing a price breakout accompanied by high volume in a single 5-minute candle, the trader can quickly enter a position to capitalize on immediate momentum.

---

### Sample JSON Response

```json
[
  {
    "date": "2025-02-04 15:55:00",
    "open": 232.87,
    "low": 232.72,
    "high": 233.13,
    "close": 232.79,
    "volume": 1555040
  }
]

```