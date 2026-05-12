# Income Statements TTM API

The **Income Statements TTM (Trailing Twelve Months)** API provides financial data representing a company's performance over the 12 most recent months. This is essential for analyzing the most current financial trends without waiting for a full fiscal year report.

---

## About Income Statements TTM API

Trailing Twelve Months (TTM) figures are used by investors and analysts to evaluate a company's most recent financial health. By aggregating the last four quarters of data, this API offers a normalized view of revenue, expenses, and profitability that accounts for seasonality.

### Endpoint

```http
https://financialmodelingprep.com/stable/income-statement-ttm?symbol=AAPL

```

---

## API Parameters

| Query Parameter | Type | Example | Description |
| --- | --- | --- | --- |
| `symbol`* | string | AAPL | The stock ticker symbol of the company. |
| `limit` | number | 5 | The number of TTM records to retrieve. |

**Notes:**

* `*` indicates a **Required** parameter.
* **Maximum Records:** 1,000 records per request.
* **Currency:** All financial values are reported in the company's reported currency (e.g., USD).

---

## Example Response

```json
[
  {
    "date": "2024-12-28",
    "symbol": "AAPL",
    "reportedCurrency": "USD",
    "cik": "0000320193",
    "filingDate": "2025-01-31",
    "acceptedDate": "2025-01-31 06:01:27",
    "fiscalYear": "2025",
    "period": "Q1",
    "revenue": 395760000000,
    "costOfRevenue": 211657000000,
    "grossProfit": 184103000000,
    "researchAndDevelopmentExpenses": 31942000000,
    "generalAndAdministrativeExpenses": 0,
    "sellingAndMarketingExpenses": 0,
    "sellingGeneralAndAdministrativeExpenses": 26486000000,
    "otherExpenses": 0,
    "operatingExpenses": 58428000000,
    "costAndExpenses": 270085000000,
    "netInterestIncome": 0,
    "interestIncome": 0,
    "interestExpense": 0,
    "depreciationAndAmortization": 11677000000,
    "ebitda": 137352000000,
    "ebit": 125675000000,
    "nonOperatingIncomeExcludingInterest": 0,
    "operatingIncome": 125675000000,
    "totalOtherIncomeExpensesNet": 71000000,
    "incomeBeforeTax": 125746000000,
    "incomeTaxExpense": 29596000000,
    "netIncomeFromContinuingOperations": 96150000000,
    "netIncomeFromDiscontinuedOperations": 0,
    "otherAdjustmentsToNetIncome": 0,
    "netIncome": 96150000000,
    "netIncomeDeductions": 0,
    "bottomLineNetIncome": 96150000000,
    "eps": 6.31,
    "epsDiluted": 6.3,
    "weightedAverageShsOut": 15081724000,
    "weightedAverageShsOutDil": 15150865000
  }
]

```