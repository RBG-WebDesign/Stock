## Income Statement Growth Bulk API

The **Bulk Income Statement Growth API** provides access to growth data for income statements across multiple companies. Track and analyze growth trends over time for key financial metrics such as revenue, net income, and operating income, enabling a better understanding of corporate performance trends.

### About Income Statement Growth Bulk API

This API is ideal for users who want to:

* **Track Financial Growth:** Understand how a company’s income statement figures, like revenue and net income, are growing over time.
* **Analyze Trends:** Gain insights into long-term trends in income statement growth, including expenses, EBITDA, and earnings per share (EPS).
* **Evaluate Performance:** Measure a company’s growth rate across multiple financial metrics to evaluate its financial health and performance over time.
* **Bulk Data Retrieval:** Quickly retrieve growth data for income statements across a large number of companies for comparative analysis or trend forecasting.

---

### Endpoint

`https://financialmodelingprep.com/stable/income-statement-growth-bulk?year=2026&period=Q1`

### Income Statement Growth Bulk API Parameters

| Query Parameter | Type | Example |
| --- | --- | --- |
| **year*** | string | 2026 |
| **period*** | string | Q1, Q2, Q3, Q4, or FY |

`(*)` Required

### Response Example

```json
[
	{
		"symbol": "000001.SZ",
		"date": "2025-03-31",
		"fiscalYear": "2025",
		"period": "Q1",
		"reportedCurrency": "CNY",
		"growthRevenue": "-0.04159070191431176",
		"growthCostOfRevenue": "0",
		"growthGrossProfit": "-0.04159070191431176",
		"growthGrossProfitRatio": "0",
		"growthResearchAndDevelopmentExpenses": "0",
		"growthGeneralAndAdministrativeExpenses": "1.7466809598416757",
		"growthSellingAndMarketingExpenses": "0",
		"growthOtherExpenses": "-0.9860376183912135",
		"growthOperatingExpenses": "-0.095830920671685",
		"growthCostAndExpenses": "-0.095830920671685",
		"growthInterestIncome": "-0.003105727849505302",
		"growthInterestExpense": "-0.08421879522057303",
		"growthDepreciationAndAmortization": "0",
		"growthEBITDA": "0",
		"growthOperatingIncome": "-0.018874787810201278",
		"growthIncomeBeforeTax": "1.4139262224764084",
		"growthIncomeTaxExpense": "0.2582392776523702",
		"growthNetIncome": "1.9495710399665203",
		"growthEPS": "1.6956521739130435",
		"growthEPSDiluted": "1.6956521739130435",
		"growthWeightedAverageShsOut": "0.09825852256371011",
		"growthWeightedAverageShsOutDil": "0.09825852256371011",
		"growthEBIT": "1",
		"growthNonOperatingIncomeExcludingInterest": "-0.5659209985158163",
		"growthNetInterestIncome": "0.09080465272126753",
		"growthTotalOtherIncomeExpensesNet": "0.5835023664638269",
		"growthNetIncomeFromContinuingOperations": "1.9495710399665203",
		"growthOtherAdjustmentsToNetIncome": "0",
		"growthNetIncomeDeductions": "0"
	}
]

```