# Financial Estimates API

Retrieve analyst financial estimates for stock symbols with the **FMP Financial Estimates API**. Access projected figures like revenue, earnings per share (EPS), and other key financial metrics as forecasted by industry analysts to inform your investment decisions.

---

## About Financial Estimates API

The FMP Financial Estimates API is an invaluable resource for investors who want a deeper understanding of a company's projected performance. By collecting forecasts from leading financial analysts, this API provides essential insights into:

* **Revenue Projections:** Get estimates on future company revenue, offering a glimpse into anticipated growth trends.
* **Earnings Per Share (EPS) Forecasts:** Access analyst predictions on a company’s future earnings, which are critical for evaluating profitability.
* **Consensus Metrics:** View consensus estimates from multiple analysts, providing a comprehensive outlook on the market’s expectations.
* **Investment Planning:** Use these estimates to benchmark a company's projected performance, identify potential over- or undervalued stocks, and refine your investment strategies.

The Financial Estimates API is ideal for investors, traders, and financial analysts looking to build more accurate financial models or make informed investment decisions based on market forecasts.

**Endpoint:**

```http
https://financialmodelingprep.com/stable/analyst-estimates?symbol=AAPL&period=annual&page=0&limit=10

```

---

## Financial Estimates API Parameters

| Query Parameter | Type | Example | Description |
| --- | --- | --- | --- |
| `symbol`* | string | AAPL | The stock ticker symbol. |
| `period`* | string | `annual` | The forecast period: `annual` or `quarter`. |
| `page` | number | 0 | The page number for pagination. |
| `limit` | number | 10 | The number of records to return. |

**Notes:**

* `*` indicates a **Required** parameter.
* **Maximum Records:** 1,000 records per request.
* **Currency:** Financial values are reported in the company's reported currency.

---

## Example Response

```json
[
  {
    "symbol": "AAPL",
    "date": "2029-09-28",
    "revenueLow": 483092500000,
    "revenueHigh": 483093500000,
    "revenueAvg": 483093000000,
    "ebitdaLow": 155952166036,
    "ebitdaHigh": 155952488856,
    "ebitdaAvg": 155952327446,
    "ebitLow": 140628295747,
    "ebitHigh": 140628586847,
    "ebitAvg": 140628441297,
    "netIncomeLow": 139446957701,
    "netIncomeHigh": 157185372990,
    "netIncomeAvg": 149150359609,
    "sgaExpenseLow": 31694652812,
    "sgaExpenseHigh": 31694718420,
    "sgaExpenseAvg": 31694685616,
    "epsAvg": 9.68,
    "epsHigh": 10.20148,
    "epsLow": 9.0502
  }
]

```