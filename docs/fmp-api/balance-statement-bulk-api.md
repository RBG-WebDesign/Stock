## Balance Sheet Statement Bulk API

The **Bulk Balance Sheet Statement API** provides comprehensive access to balance sheet data across multiple companies. It enables users to analyze financial positions by retrieving key figures such as total assets, liabilities, and equity. This endpoint is ideal for comparing the financial health and stability of different companies on a large scale.

### About Balance Sheet Statement Bulk API

This API is a powerful tool for:

* **Financial Analysis:** Retrieve balance sheet data to evaluate assets, liabilities, and equity, and assess the financial health of multiple companies.
* **Bulk Data Retrieval:** Get detailed financial positions for a wide range of companies in a single request, allowing for comparative analysis and portfolio evaluation.
* **Corporate Health Assessment:** Analyze metrics such as total debt, cash and cash equivalents, net receivables, and shareholder equity to determine the strength of a company’s balance sheet.
* **Historical Tracking:** Use balance sheet data to track a company’s financial position over time, identifying trends and changes in its financial standing.

---

### Endpoint

`https://financialmodelingprep.com/stable/balance-sheet-statement-bulk?year=2026&period=Q1`

### Balance Sheet Statement Bulk API Parameters

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
		"symbol": "MTLRP.ME",
		"reportedCurrency": "RUB",
		"cik": "0000000000",
		"filingDate": "2025-05-31",
		"acceptedDate": "2025-03-31 07:00:00",
		"fiscalYear": "2025",
		"period": "Q1",
		"cashAndCashEquivalents": "1985000",
		"shortTermInvestments": "0",
		"cashAndShortTermInvestments": "1985000",
		"netReceivables": "9666577000",
		"accountsReceivables": "9666577000",
		"otherReceivables": "0",
		"inventory": "4520000",
		"prepaids": "0",
		"otherCurrentAssets": "27293000",
		"totalCurrentAssets": "9700830000",
		"propertyPlantEquipmentNet": "194000",
		"goodwill": "0",
		"intangibleAssets": "5665000",
		"goodwillAndIntangibleAssets": "5665000",
		"longTermInvestments": "237373355000",
		"taxAssets": "791813000",
		"otherNonCurrentAssets": "0",
		"totalNonCurrentAssets": "238171027000",
		"otherAssets": "0",
		"totalAssets": "247871857000",
		"totalPayables": "3861497000",
		"accountPayables": "3861497000",
		"otherPayables": "0",
		"accruedExpenses": "0",
		"shortTermDebt": "4842848000",
		"capitalLeaseObligationsCurrent": "0",
		"taxPayables": "2484576000",
		"deferredRevenue": "0",
		"otherCurrentLiabilities": "146647000",
		"totalCurrentLiabilities": "8851455000",
		"longTermDebt": "178923999000",
		"capitalLeaseObligationsNonCurrent": "0",
		"deferredRevenueNonCurrent": "0",
		"deferredTaxLiabilitiesNonCurrent": "737391000",
		"otherNonCurrentLiabilities": "52574304000",
		"totalNonCurrentLiabilities": "232235780000",
		"otherLiabilities": "0",
		"capitalLeaseObligations": "0",
		"totalLiabilities": "244087635000",
		"treasuryStock": "0",
		"preferredStock": "0",
		"commonStock": "5550277000",
		"retainedEarnings": "-5066509000",
		"additionalPaidInCapital": "6023340000",
		"accumulatedOtherComprehensiveIncomeLoss": "0",
		"otherTotalStockholdersEquity": "0",
		"totalStockholdersEquity": "6784622000",
		"totalEquity": "6784622000",
		"minorityInterest": "0",
		"totalLiabilitiesAndTotalEquity": "247871857000",
		"totalInvestments": "237373355000",
		"totalDebt": "183766847000",
		"netDebt": "183764862000"
	}
]

```