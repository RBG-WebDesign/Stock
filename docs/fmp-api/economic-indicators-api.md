## Economics Indicators API

Access real-time and historical economic data for key indicators like GDP, unemployment, and inflation with the FMP Economic Indicators API. Use this data to measure economic performance and identify growth trends.

### About Economics Indicators API

The FMP Economic Indicators API provides comprehensive access to real-time and historical data for a wide range of economic indicators. These indicators are essential tools for:

* **Economic Performance Tracking:** Economic indicators such as GDP, unemployment, and inflation provide a snapshot of the overall health of the economy. By tracking these indicators over time, investors and analysts can gauge economic performance and make predictions about future economic conditions.
* **Trend Identification:** Identifying trends in economic growth is crucial for making informed investment decisions. The Economic Indicators API allows users to analyze historical data and detect patterns that can indicate economic expansion or contraction.
* **Informed Investment Decisions:** Economic data is a key factor in making informed investment decisions. By understanding the current state of the economy and its trajectory, investors can better align their portfolios with economic cycles.

---

### Example Investor Use Case

An investor might use the Economic Indicators API to monitor GDP growth rates over the past decade. By analyzing this data, the investor can identify periods of strong economic growth and align their investment strategy accordingly.

---

### Endpoint

`https://financialmodelingprep.com/stable/economic-indicators?name=GDP`

---

### Economics Indicators API Parameters

| Query Parameter | Type | Example |
| --- | --- | --- |
| `name*` | string | `GDP`, `unemploymentRate`, `inflation`, etc. |
| `from` | date | 2025-04-27 |
| `to` | date | 2026-04-27 |

> **(*) Required** | Max 90-day date range

**Available Name Values:**
`GDP`, `realGDP`, `nominalPotentialGDP`, `realGDPPerCapita`, `federalFunds`, `CPI`, `inflationRate`, `inflation`, `retailSales`, `consumerSentiment`, `durableGoods`, `unemploymentRate`, `totalNonfarmPayroll`, `initialClaims`, `industrialProductionTotalIndex`, `newPrivatelyOwnedHousingUnitsStartedTotalUnits`, `totalVehicleSales`, `retailMoneyFunds`, `smoothedUSRecessionProbabilities`, `3MonthOr90DayRatesAndYieldsCertificatesOfDeposit`, `commercialBankInterestRateOnCreditCardPlansAllAccounts`, `30YearFixedRateMortgageAverage`, `15YearFixedRateMortgageAverage`, `tradeBalanceGoodsAndServices`

---

### Response

```json
[
	{
		"name": "GDP",
		"date": "2025-10-01",
		"value": 31442.483
	}
]

```