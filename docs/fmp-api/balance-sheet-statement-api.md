# Balance Sheet Statement API

Access detailed balance sheet statements for publicly traded companies with the **Balance Sheet Data API**. Analyze assets, liabilities, and shareholder equity to gain insights into a company's financial health.

---

## About Balance Sheet Statement API

The Balance Sheet Data API allows investors, analysts, and financial professionals to retrieve detailed balance sheet information for companies. This API is essential for:

* **Comprehensive Financial Analysis:** View key data on assets, liabilities, and shareholder equity, allowing for a detailed assessment of a company's financial structure and solvency.
* **Evaluating Company Health:** Determine a company's liquidity and leverage through short-term and long-term assets, liabilities, and shareholder equity positions.
* **Supporting Investment Decisions:** Use the balance sheet to compare companies within the same industry or sector, ensuring you make informed investment decisions based on a company's financial stability.

This API provides real-time and historical balance sheet data, offering a snapshot of a company's financial health over different periods. Whether you're analyzing a company's financial performance or conducting due diligence, this data helps you evaluate critical financial metrics with ease.

---

### Example Use Case

An investor analyzing a potential stock purchase uses the Balance Sheet Data API to evaluate the company's assets and liabilities. They review how much cash the company has on hand, its debt obligations, and total equity to ensure the company is financially stable.

### Endpoint

```http
https://financialmodelingprep.com/stable/balance-sheet-statement?symbol=AAPL

```

---

## API Parameters

| Query Parameter | Type | Example |
| --- | --- | --- |
| **symbol*** | string | `AAPL` |
| **limit** | number | `5` |
| **period** | string | `FY`, `annual`, `quarter`, `Q1`, `Q2`, `Q3`, `Q4` |

> `*` **Required** | Maximum 1,000 records per request | Currency is as Reported in Financials.

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
    "cashAndCashEquivalents": 29943000000,
    "shortTermInvestments": 35228000000,
    "cashAndShortTermInvestments": 65171000000,
    "netReceivables": 66243000000,
    "accountsReceivables": 33410000000,
    "otherReceivables": 32833000000,
    "inventory": 7286000000,
    "prepaids": 0,
    "otherCurrentAssets": 14287000000,
    "totalCurrentAssets": 152987000000,
    "propertyPlantEquipmentNet": 45680000000,
    "goodwill": 0,
    "intangibleAssets": 0,
    "goodwillAndIntangibleAssets": 0,
    "longTermInvestments": 91479000000,
    "taxAssets": 19499000000,
    "otherNonCurrentAssets": 55335000000,
    "totalNonCurrentAssets": 211993000000,
    "otherAssets": 0,
    "totalAssets": 364980000000,
    "totalPayables": 95561000000,
    "accountPayables": 68960000000,
    "otherPayables": 26601000000,
    "accruedExpenses": 0,
    "shortTermDebt": 20879000000,
    "capitalLeaseObligationsCurrent": 1632000000,
    "taxPayables": 26601000000,
    "deferredRevenue": 8249000000,
    "otherCurrentLiabilities": 50071000000,
    "totalCurrentLiabilities": 176392000000,
    "longTermDebt": 85750000000,
    "deferredRevenueNonCurrent": 10798000000,
    "deferredTaxLiabilitiesNonCurrent": 0,
    "otherNonCurrentLiabilities": 35090000000,
    "totalNonCurrentLiabilities": 131638000000,
    "otherLiabilities": 0,
    "capitalLeaseObligations": 12430000000,
    "totalLiabilities": 308030000000,
    "treasuryStock": 0,
    "preferredStock": 0,
    "commonStock": 83276000000,
    "retainedEarnings": -19154000000,
    "additionalPaidInCapital": 0,
    "accumulatedOtherComprehensiveIncomeLoss": -7172000000,
    "otherTotalStockholdersEquity": 0,
    "totalStockholdersEquity": 56950000000,
    "totalEquity": 56950000000,
    "minorityInterest": 0,
    "totalLiabilitiesAndTotalEquity": 364980000000,
    "totalInvestments": 126707000000,
    "totalDebt": 106629000000,
    "netDebt": 76686000000
  }
]

```