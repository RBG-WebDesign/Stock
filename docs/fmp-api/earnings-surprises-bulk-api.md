# Earnings Surprises Bulk API

The **Earnings Surprises Bulk API** allows users to retrieve bulk data on annual earnings surprises, enabling quick analysis of which companies have beaten, missed, or met their earnings estimates. This API provides actual versus estimated earnings per share (EPS) for multiple companies at once, offering valuable insights for investors and analysts.

### About Earnings Surprises Bulk API

The Earnings Surprises Bulk API is an essential tool for those who want to:

* **Identify Performance Trends:** Track whether companies consistently beat or miss earnings estimates.
* **Investment Opportunities:** Spot potential investment opportunities in companies that are exceeding earnings expectations or facing downward trends due to missed estimates.
* **Analyze Market Sentiment:** Gauge investor confidence by analyzing how a company's earnings performance compares to market expectations.
* **Strategic Forecasting:** Use historical data to enhance financial forecasting models or make data-driven investment decisions.

With this bulk API, you can easily retrieve earnings surprises data for multiple companies, simplifying the process of spotting trends across different industries or sectors.

---

### Endpoint

`https://financialmodelingprep.com/stable/earnings-surprises-bulk?year=2026`

### Earnings Surprises Bulk API Parameters

| Query Parameter | Type | Example |
| --- | --- | --- |
| **year*** | string | 2026 |

`(*)` Required

### Response Example

```json
[
  {
    "symbol": "AMKYF",
    "date": "2025-07-09",
    "epsActual": "0.3631",
    "epsEstimated": "0.3615",
    "lastUpdated": "2025-07-09"
  }
]

```