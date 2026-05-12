# Historical Stock Grades API

Access a comprehensive record of analyst grades with the **FMP Historical Stock Grades API**. This tool allows you to track historical changes in analyst ratings for specific stock symbols to gauge shifts in market sentiment.

---

## About Historical Stock Grades API

The FMP Historical Stock Grades API offers an in-depth look at how analysts have rated specific stocks over time. This API is essential for:

* **Trend Analysis:** Investors can use historical ratings to spot long-term trends in market sentiment, helping to predict potential price movements based on analyst consensus.
* **Investment Strategy Optimization:** By tracking changes in analyst sentiment, investors can adjust their strategies as experts become more bullish or bearish.
* **Benchmarking Performance:** Compare a stock’s historical ratings to its actual price performance to understand how well the stock has lived up to professional expectations.
* **Market Sentiment Tracking:** Analyze how the distribution of buy, hold, and sell ratings has changed, providing insight into broader market confidence or caution.

This API empowers investors with historical context, offering a valuable tool for long-term financial analysis and strategic decision-making.

---

### Example Use Case

A portfolio manager can utilize the Historical Stock Grades API to observe changes in the count of "Buy" vs. "Sell" ratings for a particular stock over several quarters, helping them determine if the prevailing expert opinion is strengthening or weakening.

**Endpoint:**

```http
https://financialmodelingprep.com/stable/grades-historical?symbol=AAPL

```

---

## Historical Stock Grades API Parameters

| Query Parameter | Type | Example | Description |
| --- | --- | --- | --- |
| `symbol`* | string | AAPL | The stock ticker symbol. |
| `limit` | number | 100 | The number of historical rating records to return. |

**Notes:**

* `*` indicates a **Required** parameter.
* **Maximum Records:** 1,000 records per request.

---

## Example Response

```json
[
  {
    "symbol": "AAPL",
    "date": "2025-02-01",
    "analystRatingsBuy": 8,
    "analystRatingsHold": 14,
    "analystRatingsSell": 2,
    "analystRatingsStrongSell": 2
  }
]

```