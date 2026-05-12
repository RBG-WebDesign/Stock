# Stock Quote API

Access real-time stock quotes with the **FMP Stock Quote API**. Get up-to-the-minute prices, changes, and volume data for individual stocks to stay ahead of market movements.

---

## About Stock Quote API

The FMP Stock Quote API provides detailed, real-time stock data for individual stocks, making it a valuable tool for investors, traders, and financial analysts. This API helps you:

* **Monitor Real-Time Prices:** Stay updated with the latest stock prices to make informed trading decisions.
* **Analyze Stock Movements:** Track key data points such as price changes, volume, day highs/lows, and yearly highs/lows.
* **Portfolio Tracking:** Use real-time data to keep track of stock performance in your portfolio.

> **Note:** Nasdaq data is delayed by 15 minutes. Real-time access requires completion of the user declaration form.

**Endpoint:**

```http
https://financialmodelingprep.com/stable/quote?symbol=AAPL

```

---

## Stock Quote API Parameters

| Query Parameter | Type | Example | Description |
| --- | --- | --- | --- |
| `symbol`* | string | AAPL | The stock ticker symbol. |

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