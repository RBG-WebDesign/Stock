# Financial Scores API

Assess a company's financial strength using the **Financial Health Scores API**. This API provides key metrics such as the **Altman Z-Score** and **Piotroski Score**, giving users insights into a company’s overall financial health and stability.

---

## About Financial Scores API

The Financial Health Scores API offers a detailed evaluation of a company's financial stability by calculating various proprietary and academic scores. This API is essential for:

* **Bankruptcy Risk Analysis:** Utilize the **Altman Z-Score** to predict the likelihood of a company entering bankruptcy within two years.
* *Safe Zone:* > 2.99
* *Grey Zone:* 1.81 - 2.99
* *Distress Zone:* < 1.81


* **Profitability and Efficiency Evaluation:** Use the **Piotroski Score** (F-Score), a 9-point scale used to determine the strength of a firm's financial position based on profitability, leverage, and operating efficiency.
* *Strong:* 8–9 points
* *Weak:* 0–2 points


* **Working Capital Management:** Track changes in working capital to understand how a company manages its short-term assets and liabilities.
* **Leverage and Capital Structure:** Assess the relationship between total liabilities and market capitalization to evaluate financial leverage.

This API is a powerful tool for investors and analysts who need to evaluate the financial strength of a company to make informed, data-driven decisions.

---

### Example Use Case

A financial analyst uses the Financial Health Scores API to check a company's Altman Z-Score and Piotroski Score before recommending it as a stable investment to clients. High scores in both areas often signal a robust, well-managed company.

**Endpoint:**

```http
https://financialmodelingprep.com/stable/financial-scores?symbol=AAPL

```

---

## Financial Scores API Parameters

| Query Parameter | Type | Example | Description |
| --- | --- | --- | --- |
| `symbol`* | string | AAPL | The stock ticker symbol. |

**Notes:**

* `*` indicates a **Required** parameter.
* **Currency:** Financial values used in calculations are as **Reported in Financials**.

---

## Example Response

```json
[
  {
    "symbol": "AAPL",
    "reportedCurrency": "USD",
    "altmanZScore": 9.322985825443649,
    "piotroskiScore": 8,
    "workingCapital": -11125000000,
    "totalAssets": 344085000000,
    "retainedEarnings": -11221000000,
    "ebit": 125675000000,
    "marketCap": 3259495258000,
    "totalLiabilities": 277327000000,
    "revenue": 395760000000
  }
]

```