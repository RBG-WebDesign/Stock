## Income Statement Bulk API

The **Bulk Income Statement API** allows users to retrieve detailed income statement data in bulk. This API is designed for large-scale data analysis, providing comprehensive insights into a company's financial performance, including revenue, gross profit, expenses, and net income.

### About Income Statement Bulk API

The Bulk Income Statement API is ideal for users who need to:

* **Analyze Financial Performance:** Access large datasets for deep financial analysis, including multiple income statements from various companies.
* **Track Revenue and Profit Trends:** Quickly retrieve data on revenue, gross profit, operating income, and net income to assess a company's profitability over time.
* **Evaluate Expenses:** Review operating expenses, cost of revenue, and selling, general, and administrative expenses (SG&A) to identify where a company allocates its spending.
* **Conduct Bulk Research:** Ideal for financial analysts, investors, and researchers who need to process income statements across multiple companies for detailed industry or sector comparison.

This API delivers financial data in a standardized format, making it easy to conduct large-scale financial analysis.

---

### Endpoint

`https://financialmodelingprep.com/stable/income-statement-bulk?year=2026&period=Q1`

### Income Statement Bulk API Parameters

| Query Parameter | Type | Example |
| --- | --- | --- |
| **year*** | string | 2026 |
| **period*** | string | Q1, Q2, Q3, Q4, or FY |

`(*)` Required

### Response Example

```json
[
  {
    "date": "2025-03-31",
    "symbol": "000001.SZ",
    "reportedCurrency": "CNY",
    "cik": "0000000000",
    "filingDate": "2025-03-31",
    "acceptedDate": "2025-03-31 00:00:00",
    "fiscalYear": "2025",
    "period": "Q1",
    "revenue": "33644000000",
    "costOfRevenue": "0",
    "grossProfit": "33644000000",
    "researchAndDevelopmentExpenses": "0",
    "generalAndAdministrativeExpenses": "9055000000",
    "sellingAndMarketingExpenses": "0",
    "sellingGeneralAndAdministrativeExpenses": "9055000000",
    "otherExpenses": "314000000",
    "operatingExpenses": "9369000000",
    "costAndExpenses": "9369000000",
    "netInterestIncome": "22788000000",
    "interestIncome": "44938000000",
    "interestExpense": "22150000000",
    "depreciationAndAmortization": "0",
    "ebitda": "16802000000",
    "ebit": "0",
    "nonOperatingIncomeExcludingInterest": "24275000000",
    "operatingIncome": "24275000000",
    "totalOtherIncomeExpensesNet": "-7392000000",
    "incomeBeforeTax": "16883000000",
    "incomeTaxExpense": "2787000000",
    "netIncomeFromContinuingOperations": "14096000000",
    "netIncomeFromDiscontinuedOperations": "0",
    "otherAdjustmentsToNetIncome": "0",
    "netIncome": "14096000000",
    "netIncomeDeductions": "0",
    "bottomLineNetIncome": "14096000000",
    "eps": "0.62",
    "epsDiluted": "0.62",
    "weightedAverageShsOut": "22735483871",
    "weightedAverageShsOutDil": "22735483871"
  }
]

```