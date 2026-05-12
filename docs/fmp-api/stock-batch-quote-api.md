# Stock Batch Quote API

Retrieve multiple real-time stock quotes in a single request with the **FMP Stock Batch Quote API**. Access current prices, volume, and detailed data for multiple companies at once, making it easier to track large portfolios or monitor multiple stocks simultaneously.

---

## About Stock Batch Quote API

The FMP Stock Batch Quote API allows users to retrieve quotes for multiple stocks in one streamlined request. This API is ideal for:

* **Portfolio Monitoring:** Track several stocks in real-time—perfect for investors or portfolio managers who need to monitor multiple holdings at once.
* **Data Efficiency:** Instead of making multiple calls, get detailed stock data for several companies in a single API request, reducing complexity and latency.
* **Comprehensive Stock Insights:** Access detailed data for each stock, including the current price, volume, day high/low, 50-day and 200-day moving averages, and more.

This API ensures efficient data retrieval for investors, traders, and applications requiring comprehensive real-time stock data for multiple symbols.

> **Note:** Nasdaq data is delayed by 15 minutes. Real-time access requires completion of the [user declaration form](https://www.google.com/search?q=https://financialmodelingprep.com/user-declaration-form).

---

### Endpoint

```http
https://financialmodelingprep.com/stable/batch-quote?symbols=AAPL,MSFT,GOOGL

```

---

## Stock Batch Quote API Parameters

| Query Parameter | Type | Example | Description |
| --- | --- | --- | --- |
| `symbols`* | string | AAPL,MSFT | A comma-separated list of stock ticker symbols. |

**Notes:**

* `*` indicates a **Required** parameter.

---

## Example Response

```json
[
  {
    "symbol": "AAPL",
    "name": "Apple Inc.",
    "price": 232.8,
    "changePercentage": 2.1008,
    "change": 4.79,
    "volume": 44489128,
    "dayLow": 226.65,
    "dayHigh": 233.13,
    "yearHigh": 260.1,
    "yearLow": 164.08,
    "marketCap": 3500823120000,
    "priceAvg50": 240.2278,
    "priceAvg200": 219.98755,
    "exchange": "NASDAQ",
    "open": 227.2,
    "previousClose": 228.01,
    "timestamp": 1738702801
  }
]

```