# 30-Minute Interval Stock Chart API

The **Financial Modeling Prep (FMP)** 30-Minute Interval Stock Chart API provides precise intraday price and volume data. It is engineered for traders who need a "birds-eye view" of the trading day, offering enough detail to spot trends without the volatility noise found in 1-minute or 5-minute charts.

---

### Key Features

* **Efficient Medium-Term Analysis:** Provides a balanced view of stock performance, filtering out micro-fluctuations.
* **Comprehensive Data Points:** Includes Open, High, Low, Close (OHLC), and trading volume for every 30-minute block.
* **Strategy Optimization:** Ideal for intraday strategies that rely on sustained price movements and volume clusters.
* **Historical Trends:** Access past 30-minute interval data to backtest strategies or analyze historical volatility patterns.

---

### API Reference

**Endpoint URL**
`https://financialmodelingprep.com/stable/historical-chart/30min?symbol=AAPL`

#### Query Parameters

| Parameter | Type | Required | Example | Description |
| --- | --- | --- | --- | --- |
| **symbol** | string | Yes | `AAPL` | The ticker symbol of the stock. |
| **from** | date | No | `2024-01-01` | The start date for the data range. |
| **to** | date | No | `2024-03-01` | The end date for the data range. |
| **nonadjusted** | boolean | No | `false` | Whether to return non-adjusted data. |

---

> **Example Use Case**
> A day trader utilizes this API to monitor **Apple (AAPL)**. By analyzing 30-minute candles, they can identify whether a morning breakout has enough volume support to hold through the afternoon, helping them make more calculated entry and exit decisions.

---

### Sample JSON Response

```json
[
  {
    "date": "2025-02-04 15:30:00",
    "open": 232.29,
    "low": 232.01,
    "high": 233.13,
    "close": 232.79,
    "volume": 3476320
  }
]

```