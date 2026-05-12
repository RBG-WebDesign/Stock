# Price Target Summary API

Gain insights into analysts' expectations for stock prices with the **FMP Price Target Summary API**. This API provides access to average price targets from analysts across various timeframes, helping investors assess future stock performance based on expert opinions.

---

## About Price Target Summary API

The FMP Price Target Summary API allows users to track and analyze analysts' price targets for individual stocks, making it a valuable tool for investors and analysts looking to understand market sentiment. Key features include:

* **Average Price Targets:** Access average price targets from analysts over different periods (last month, last quarter, last year, and all time).
* **Price Target History:** Track how price expectations have evolved over time to gauge changes in analysts' outlooks.
* **Analyst Coverage:** Retrieve the number of analysts providing price targets during specific periods.
* **Multiple Publishers:** View a list of sources and publishers providing price target data, such as Benzinga, MarketWatch, and Barrons.

This API allows you to quickly assess the consensus among financial analysts regarding a stock’s future price movement.

---

### Example Use Case

An investor can use the Price Target Summary API to compare the average price targets for a stock over the past quarter and year to determine if analysts' outlooks have become more bullish or bearish over time.

**Endpoint:**

```http
https://financialmodelingprep.com/stable/price-target-summary?symbol=AAPL

```

---

## Price Target Summary API Parameters

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
    "lastMonthCount": 1,
    "lastMonthAvgPriceTarget": 200.75,
    "lastQuarterCount": 3,
    "lastQuarterAvgPriceTarget": 204.2,
    "lastYearCount": 48,
    "lastYearAvgPriceTarget": 232.99,
    "allTimeCount": 167,
    "allTimeAvgPriceTarget": 201.21,
    "publishers": "[\"Benzinga\",\"StreetInsider\",\"TheFly\",\"Pulse 2.0\",\"TipRanks Contributor\",\"MarketWatch\",\"Investing\",\"Barrons\",\"Investor's Business Daily\"]"
  }
]

```