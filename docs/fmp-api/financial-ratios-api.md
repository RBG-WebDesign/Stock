# Financial Ratios API

Analyze a company's financial performance using the **Financial Ratios API**. This API provides detailed profitability, liquidity, and efficiency ratios, enabling users to assess a company's operational and financial health across various metrics.

---

## About Financial Ratios API

The Financial Ratios API delivers key ratios that help investors, analysts, and researchers evaluate a company's performance. This API offers a comprehensive view of a company's financial health and operational efficiency through several categories:

* **Profitability Ratios:** Gain insight into a company's ability to generate profit, with metrics like net profit margin and return on equity.
* **Liquidity Ratios:** Understand how well a company can meet its short-term obligations using ratios like current ratio and quick ratio.
* **Efficiency Ratios:** Assess how effectively a company utilizes its assets with metrics such as asset turnover and inventory turnover.
* **Debt Ratios:** Evaluate a company's leverage and debt management through ratios like debt-to-equity and interest coverage ratios.

---

### Example Use Case

A portfolio manager can use the Financial Ratios API to compare liquidity ratios between companies in the same industry, helping them identify firms with stronger financial stability and more efficient operations.

**Endpoint:**

```http
https://financialmodelingprep.com/stable/ratios?symbol=AAPL

```

---

## Financial Ratios API Parameters

| Query Parameter | Type | Example | Description |
| --- | --- | --- | --- |
| `symbol`* | string | AAPL | The stock ticker symbol. |
| `limit` | number | 5 | Number of records to return. |
| `period` | string | `annual` | Period of the report: `Q1`, `Q2`, `Q3`, `Q4`, `FY`, `annual`, or `quarter`. |

**Notes:**

* `*` indicates a **Required** parameter.
* **Maximum Records:** 1,000 records per request.
* **Currency:** Ratios are derived from financials reported in the company's base currency.

---

## Example Response

```json
[
  {
    "symbol": "AAPL",
    "date": "2024-09-28",
    "fiscalYear": "2024",
    "period": "FY",
    "reportedCurrency": "USD",
    "grossProfitMargin": 0.4620634981523393,
    "ebitMargin": 0.31510222870075566,
    "ebitdaMargin": 0.3443707085043538,
    "operatingProfitMargin": 0.31510222870075566,
    "pretaxProfitMargin": 0.3157901466620635,
    "continuousOperationsProfitMargin": 0.23971255769943867,
    "netProfitMargin": 0.23971255769943867,
    "bottomLineProfitMargin": 0.23971255769943867,
    "receivablesTurnover": 5.903038811648023,
    "payablesTurnover": 3.0503480278422272,
    "inventoryTurnover": 28.870710952511665,
    "fixedAssetTurnover": 8.560310858143607,
    "assetTurnover": 1.0713874732862074,
    "currentRatio": 0.8673125765340832
  }
]

```