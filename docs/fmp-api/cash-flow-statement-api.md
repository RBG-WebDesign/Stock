# Cash Flow Statement API

Gain insights into a company's cash flow activities with the **Cash Flow Statements API**. Analyze cash generated and used from operations, investments, and financing activities to evaluate the financial health and sustainability of a business.

---

## About Cash Flow Statement API

The Cash Flow Statements API provides a detailed view of a company's cash flow, giving investors and analysts essential data to understand how a company generates and spends its cash. This API is critical for:

* **Assessing Financial Health:** Evaluate a company’s ability to generate cash from its core operations and its reliance on investments and financing.
* **Understanding Cash Management:** Track cash inflows and outflows from operating, investing, and financing activities to understand how well a company manages its cash resources.
* **Free Cash Flow Analysis:** Analyze free cash flow to determine how much cash a company has left over after paying for capital expenditures, providing a clearer picture of financial flexibility.

This API delivers real-time and historical cash flow data, offering a comprehensive look at how a company manages its cash, which is essential for investment decisions, financial modeling, and credit analysis.

---

### Example Use Case

A financial analyst uses the Cash Flow Statements API to evaluate a company's operating cash flow and free cash flow, helping to assess whether the company can sustain operations, invest in growth, and return value to shareholders.

**Endpoint:**

```http
https://financialmodelingprep.com/stable/cash-flow-statement?symbol=AAPL

```

---

## Cash Flow Statement API Parameters

| Query Parameter | Type | Example |
| --- | --- | --- |
| `symbol`* | string | `AAPL` |
| `limit` | number | `5` |
| `period` | string | `Q1`, `Q2`, `Q3`, `Q4`, `FY`, `annual`, `quarter` |

`*` **Required** | Maximum 1,000 records per request | Currency is as Reported in Financials

---

## Example Response

```json
[
	{
		"date": "2024-09-28",
		"symbol": "AAPL",
		"reportedCurrency": "USD",
		"cik": "0000320193",
		"filingDate": "2024-11-01",
		"acceptedDate": "2024-11-01 06:01:36",
		"fiscalYear": "2024",
		"period": "FY",
		"netIncome": 93736000000,
		"depreciationAndAmortization": 11445000000,
		"deferredIncomeTax": 0,
		"stockBasedCompensation": 11688000000,
		"changeInWorkingCapital": 3651000000,
		"accountsReceivables": -5144000000,
		"inventory": -1046000000,
		"accountsPayables": 6020000000,
		"otherWorkingCapital": 3821000000,
		"otherNonCashItems": -2266000000,
		"netCashProvidedByOperatingActivities": 118254000000,
		"investmentsInPropertyPlantAndEquipment": -9447000000,
		"acquisitionsNet": 0,
		"purchasesOfInvestments": -48656000000,
		"salesMaturitiesOfInvestments": 62346000000,
		"otherInvestingActivities": -1308000000,
		"netCashProvidedByInvestingActivities": 2935000000,
		"netDebtIssuance": -5998000000,
		"longTermNetDebtIssuance": -9958000000,
		"shortTermNetDebtIssuance": 3960000000,
		"netStockIssuance": -94949000000,
		"netCommonStockIssuance": -94949000000,
		"commonStockIssuance": 0,
		"commonStockRepurchased": -94949000000,
		"netPreferredStockIssuance": 0,
		"netDividendsPaid": -15234000000,
		"commonDividendsPaid": -15234000000,
		"preferredDividendsPaid": 0,
		"otherFinancingActivities": -5802000000,
		"netCashProvidedByFinancingActivities": -121983000000,
		"effectOfForexChangesOnCash": 0,
		"netChangeInCash": -794000000,
		"cashAtEndOfPeriod": 29943000000,
		"cashAtBeginningOfPeriod": 30737000000,
		"operatingCashFlow": 118254000000,
		"capitalExpenditure": -9447000000,
		"freeCashFlow": 108807000000,
		"incomeTaxesPaid": 26102000000,
		"interestPaid": 0
	}
]

```