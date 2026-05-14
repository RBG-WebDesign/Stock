## Financial Scores Bulk API

The FMP Scores Bulk API allows users to quickly retrieve a wide range of key financial scores and metrics for multiple symbols. These scores provide valuable insights into company performance, financial health, and operational efficiency.

### About Financial Scores Bulk API

The Scores Bulk API delivers comprehensive financial data, enabling users to analyze the following key metrics:

* **Altman Z-Score:** Evaluate a company's likelihood of bankruptcy using this key solvency metric.
* **Piotroski Score:** Assess a company's financial strength and performance based on nine criteria.
* **Working Capital & Total Assets:** Gain insights into a company’s short-term financial health and asset base.
* **Retained Earnings and EBIT:** Understand the company's profitability and retained earnings.
* **Market Capitalization & Liabilities:** Compare company valuations and debt obligations to gauge financial stability.

This API is designed for financial analysts, investors, and institutions who need to evaluate and compare multiple companies at once, making it an efficient solution for bulk financial data retrieval.

---

### Endpoint

`https://financialmodelingprep.com/stable/scores-bulk`

---

### Response

```json
[
	{
		"symbol": "000001.SZ",
		"reportedCurrency": "CNY",
		"altmanZScore": "0.29153682196643543",
		"piotroskiScore": "5",
		"workingCapital": "746131000000",
		"totalAssets": "5777858000000",
		"retainedEarnings": "255621000000",
		"ebit": "32590000000",
		"marketCap": "236751980000",
		"totalLiabilities": "5271746000000",
		"revenue": "167996000000"
	}
]

```