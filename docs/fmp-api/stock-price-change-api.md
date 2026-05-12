# Stock Price Change API

Track stock price fluctuations in real-time with the **FMP Stock Price Change API**. Monitor percentage and value changes over various time periods, including daily, weekly, monthly, and long-term.

---

## About Stock Price Change API

The FMP Stock Price Change API allows you to stay updated on the real-time performance of stocks by tracking price changes across multiple timeframes. This API is essential for:

* **Real-Time Monitoring:** Track percentage and value changes in stock prices over different time intervals, such as 1 day, 5 days, 1 month, and up to 10 years.
* **Investment Strategy:** Use the data to identify trends in stock performance, helping you make informed decisions based on short-term and long-term price movements.
* **Comparative Analysis:** Compare price changes across multiple timeframes to assess a stock’s performance over time, helping you adjust your portfolio or strategy accordingly.

This API is a valuable resource for investors, traders, and analysts who need detailed stock performance data to inform their strategies and decisions.

**Endpoint:**

```http
https://financialmodelingprep.com/stable/stock-price-change?symbol=AAPL

```

---

## Stock Price Change API Parameters

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
    "1D": 2.1008,
    "5D": -2.45946,
    "1M": -4.33925,
    "3M": 4.86014,
    "6M": 5.88556,
    "ytd": -4.53147,
    "1Y": 24.04092,
    "3Y": 35.04264,
    "5Y": 192.05871,
    "10Y": 678.8558,
    "max": 181279.04168
  }
]

```