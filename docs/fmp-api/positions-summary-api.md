# Positions Summary API

The **Positions Summary API** provides a comprehensive snapshot of institutional holdings for a specific stock symbol. It tracks key metrics like the number of investors holding the stock, changes in the number of shares, total investment value, and ownership percentages over time.

---

## About Positions Summary API

The Positions Summary API enables users to analyze institutional positions in a particular stock by providing data such as the number of investors holding the stock, the number of shares held, the total amount invested, and changes in these metrics over a given time period. It is ideal for:

* **Tracking Institutional Investment Trends:** Monitor how institutional investors are changing their positions in a stock over time.
* **Ownership Insights:** Understand what percentage of a company is owned by institutional investors and how this ownership fluctuates.
* **Call & Put Analysis:** Get insights into the put/call ratio and track options activity for institutional positions.

This API is essential for understanding institutional activity in the market and gaining insights into the behavior of major investors. It is a vital tool for investors, analysts, and portfolio managers who need to monitor institutional movements in specific stocks.

---

### Example Use Case

A hedge fund manager can use the Positions Summary API to track institutional ownership trends in Apple (AAPL), monitoring how many institutions are increasing or reducing their positions, and assessing overall market sentiment.

**Endpoint:**

```http
https://financialmodelingprep.com/stable/institutional-ownership/symbol-positions-summary?symbol=AAPL&year=2023&quarter=3

```

---

## Positions Summary API Parameters

| Query Parameter | Type | Example | Description |
| --- | --- | --- | --- |
| `symbol`* | string | AAPL | The stock ticker symbol. |
| `year`* | string | 2023 | The specific year for the summary. |
| `quarter`* | string | 3 | The specific quarter for the summary (1-4). |

**Notes:**

* `*` indicates a **Required** parameter.

---

## Example Response

```json
[
  {
    "symbol": "AAPL",
    "cik": "0000320193",
    "date": "2023-09-30",
    "investorsHolding": 4805,
    "lastInvestorsHolding": 4749,
    "investorsHoldingChange": 56,
    "numberOf13Fshares": 9247670386,
    "lastNumberOf13Fshares": 9345671472,
    "numberOf13FsharesChange": -98001086,
    "totalInvested": 1613733330618,
    "lastTotalInvested": 1825154796061,
    "totalInvestedChange": -211421465443,
    "ownershipPercent": 59.2821,
    "lastOwnershipPercent": 59.5356,
    "ownershipPercentChange": -0.2535,
    "newPositions": 158,
    "lastNewPositions": 188,
    "newPositionsChange": -30,
    "increasedPositions": 1921,
    "lastIncreasedPositions": 1775,
    "increasedPositionsChange": 146,
    "closedPositions": 156,
    "lastClosedPositions": 122,
    "closedPositionsChange": 34,
    "reducedPositions": 2375,
    "lastReducedPositions": 2506,
    "reducedPositionsChange": -131,
    "totalCalls": 173528138,
    "lastTotalCalls": 198746782,
    "totalCallsChange": -25218644,
    "totalPuts": 192878290,
    "lastTotalPuts": 177007062,
    "totalPutsChange": 15871228,
    "putCallRatio": 1.1115,
    "lastPutCallRatio": 0.8906,
    "putCallRatioChange": 22.0894
  }
]

```