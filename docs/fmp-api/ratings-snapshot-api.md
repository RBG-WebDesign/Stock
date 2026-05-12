# Ratings Snapshot API

Quickly assess the financial health and performance of companies with the **FMP Ratings Snapshot API**. This API provides a comprehensive snapshot of financial ratings for stock symbols in our database, based on various key financial ratios.

---

## About Ratings Snapshot API

The FMP Ratings Snapshot API allows users to evaluate a company's financial performance across multiple dimensions by delivering:

* **Overall Rating:** A summary score reflecting the company's total financial standing.
* **Discounted Cash Flow (DCF) Score:** Insights into the company’s valuation relative to its future cash flow potential.
* **Return on Equity (ROE) Score:** Measures efficiency in generating profit relative to shareholders' equity.
* **Return on Assets (ROA) Score:** Gauges how effectively assets are used to generate earnings.
* **Debt-to-Equity Score:** Analyzes capital structure and risk by comparing debt to equity.
* **Price-to-Earnings (P/E) Score:** Assesses stock price relative to earnings.
* **Price-to-Book (P/B) Score:** Compares market price to book value to evaluate investment opportunities.

This API is perfect for investors, financial analysts, and researchers who need a fast, comprehensive view of a company’s financial health based on standardized metrics.

---

### Example Use Case

An equity analyst can use the Ratings Snapshot API to compare multiple companies' financial health based on return on equity, debt levels, and valuation ratios, helping them make more informed investment recommendations.

**Endpoint:**

```http
https://financialmodelingprep.com/stable/ratings-snapshot?symbol=AAPL

```

---

## Ratings Snapshot API Parameters

| Query Parameter | Type | Example | Description |
| --- | --- | --- | --- |
| `symbol`* | string | AAPL | The stock ticker symbol. |

**Notes:**

* `*` indicates a **Required** parameter.
* **Maximum Records:** 1 record per request.

---

## Example Response

```json
[
  {
    "symbol": "AAPL",
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