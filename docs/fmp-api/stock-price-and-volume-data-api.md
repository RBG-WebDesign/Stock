# Stock Price and Volume Data API

Access full price and volume data for any stock symbol using the **FMP Comprehensive Stock Price and Volume Data API**. Get detailed insights, including open, high, low, close prices, trading volume, price changes, percentage changes, and volume-weighted average price (VWAP).

---

## About Stock Price and Volume Data API

The FMP Comprehensive Stock Price and Volume Data API provides in-depth data on stock performance over time, making it an essential tool for analysts, traders, and investors. With this API, users can access:

* **Detailed Price Data:** Access complete price information, including opening, closing, high, and low prices (OHLC) for each trading day.
* **Trading Volume Insights:** Retrieve data on daily trading volume to analyze liquidity and market activity.
* **Price Changes and Percentages:** Track absolute price changes and percentage shifts to evaluate volatility and price movements.
* **VWAP (Volume-Weighted Average Price):** Get the VWAP to measure the average price based on both volume and price, helping to identify intraday trends and institutional trading behavior.

This API is perfect for users who require detailed and accurate historical data to build charts, backtest strategies, or make informed investment decisions.

---

### Example Use Case

A financial analyst can use the Comprehensive Stock Price and Volume Data API to monitor Apple's daily stock performance, analyzing price changes, VWAP, and trading volume to spot trends and predict future price movements.

**Endpoint:**

```http
https://financialmodelingprep.com/stable/historical-price-eod/full?symbol=AAPL

```

---

## Stock Price and Volume Data API Parameters

| Query Parameter | Type | Example | Description |
| --- | --- | --- | --- |
| `symbol`* | string | AAPL | The stock ticker symbol. |
| `from` | date | 2026-01-27 | The start date for the data range (YYYY-MM-DD). |
| `to` | date | 2026-04-27 | The end date for the data range (YYYY-MM-DD). |

**Notes:**

* `*` indicates a **Required** parameter.
* **Maximum Records:** 5,000 records per request.

---

## Example Response

```json
[
  {
    "symbol": "AAPL",
    "date": "2025-02-04",
    "open": 227.2,
    "high": 233.13,
    "low": 226.65,
    "close": 232.8,
    "volume": 44489128,
    "change": 5.6,
    "changePercent": 2.46479,
    "vwap": 230.86
  }
]

```