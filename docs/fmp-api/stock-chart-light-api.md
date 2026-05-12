# Stock Chart Light API

Access simplified stock chart data using the **FMP Basic Stock Chart API**. This API provides essential charting information, including date, price, and trading volume, making it ideal for tracking stock performance with minimal data overhead and creating basic price and volume charts.

---

## About Stock Chart Light API

The FMP Basic Stock Chart API delivers streamlined access to stock charting data for users who need to track price movements without overwhelming complexity. This API offers:

* **Date & Price Information:** Easily track daily price movements for a specific stock symbol.
* **Volume Data:** Stay informed about trading activity with volume data included for each date.
* **Basic Charting Needs:** Ideal for generating simple stock price and volume charts for historical performance analysis.

This API is perfect for users and developers who want a quick, straightforward way to visualize stock data without the need for detailed technical indicators or extra OHLC (Open, High, Low) data points.

---

### Example Use Case

A financial app can use the Basic Stock Chart API to display a minimal chart showing a stock’s daily closing price and volume, allowing users to quickly assess its performance over time.

**Endpoint:**

```http
https://financialmodelingprep.com/stable/historical-price-eod/light?symbol=AAPL

```

---

## Stock Chart Light API Parameters

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
    "price": 232.8,
    "volume": 44489128
  }
]

```