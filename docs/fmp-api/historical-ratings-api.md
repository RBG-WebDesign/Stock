# Historical Ratings API

Track changes in financial performance over time with the **FMP Historical Ratings API**. This API provides access to historical financial ratings for stock symbols in our database, allowing users to view ratings and key financial metric scores for specific dates.

---

## About Historical Ratings API

The FMP Historical Ratings API is ideal for analysts and investors looking to assess how a company’s financial health has evolved. By retrieving data for specific dates, you can conduct trend analysis on several key dimensions:

* **Historical Ratings:** Retrieve ratings from past dates to track a company's financial trajectory.
* **Overall Rating:** Access a summary rating representing the company’s total financial health on a given date.
* **Discounted Cash Flow (DCF) Score:** Evaluate historical valuation compared to future cash flow potential.
* **Return on Equity (ROE) Score:** Track past performance on generating profit relative to shareholders' equity.
* **Return on Assets (ROA) Score:** View how asset utilization efficiency has changed over time.
* **Debt-to-Equity Score:** Examine historical changes in the company’s capital structure and leverage.
* **Price-to-Earnings (P/E) Score:** Monitor historical stock valuation relative to earnings.
* **Price-to-Book (P/B) Score:** Assess how market price has compared to book value in the past.

---

### Example Use Case

A portfolio manager can use the Historical Ratings API to analyze how a company’s return on equity and debt-to-equity ratios have evolved over the last five years, helping them evaluate long-term performance trends and stability.

**Endpoint:**

```http
https://financialmodelingprep.com/stable/ratings-historical?symbol=AAPL

```

---

## Historical Ratings API Parameters

| Query Parameter | Type | Example | Description |
| --- | --- | --- | --- |
| `symbol`* | string | AAPL | The stock ticker symbol. |
| `limit` | number | 1 | The number of historical records to return. |

**Notes:**

* `*` indicates a **Required** parameter.
* **Maximum Records:** 10,000 records per request.

---

## Example Response

```json
[
  {
    "symbol": "AAPL",
    "date": "2025-02-04",
    "rating": "A-",
    "overallScore": 4,
    "discountedCashFlowScore": 3,
    "returnOnEquityScore": 5,
    "returnOnAssetsScore": 5,
    "debtToEquityScore": 4,
    "priceToEarningsScore": 2,
    "priceToBookScore": 1
  }
]

```