# Stock Peer Comparison API

Identify and compare companies within the same sector and market capitalization range using the **FMP Stock Peer Comparison API**. Gain insights into how a company stacks up against its peers on the same exchange.

---

## About Stock Peer Comparison API

The FMP Stock Peer Comparison API provides a curated list of companies that trade on the same exchange, belong to the same sector, and have a similar market capitalization. This API is essential for:

* **Competitive Analysis:** Compare a company’s performance against its peers to identify industry leaders and laggards.
* **Sector-Specific Insights:** Obtain relevant comparisons by focusing on companies within the same sector and market cap range, facilitating more accurate assessments of market positioning.
* **Investment Strategy:** Refine your strategy by identifying strong performers or discovering undervalued companies with growth potential.

This API is a valuable resource for investors seeking to conduct in-depth competitive analysis and make informed decisions based on relative performance.

---

### Example Use Case: Performance Benchmarking

An investor might use the Stock Peer Comparison API to compare the revenue growth and earnings per share (EPS) of a technology company to those of its peers. This helps determine whether the company is a market leader or falling behind its competitors.

**Endpoint:**

```http
https://financialmodelingprep.com/stable/stock-peers?symbol=AAPL

```

---

## Stock Peer Comparison API Parameters

| Query Parameter | Type | Example | Description |
| --- | --- | --- | --- |
| `symbol`* | string | AAPL | The stock ticker symbol. |

**Notes:**

* `*` indicates a **Required** parameter.

---

## Example Response

```json
[
  {
    "symbol": "GOOGL",
    "companyName": "Alphabet Inc.",
    "price": 317.32,
    "mktCap": 3838620208180
  }
]

```