## Economic Data Releases Calendar API

Stay informed with the FMP Economic Data Releases Calendar API. Access a comprehensive calendar of upcoming economic data releases to prepare for market impacts and make informed investment decisions.

### About Economic Data Releases Calendar API

The FMP Economic Data Releases Calendar API provides a detailed schedule of upcoming economic data releases. This tool is essential for investors who want to:

* **Stay Updated on Economic Events:** Access a calendar that lists the dates and details of key economic data releases.
* **Prepare for Market Reactions:** Anticipate market movements by staying informed about upcoming economic indicators and reports.
* **Make Informed Investment Decisions:** Use the latest economic data to guide your investment strategies and decisions.

This API is ideal for traders, analysts, and investors who need to stay ahead of market trends by monitoring critical economic data releases.

---

### Endpoint

`https://financialmodelingprep.com/stable/economic-calendar`

---

### Economic Data Releases Calendar API Parameters

| Query Parameter | Type | Example |
| --- | --- | --- |
| `country` | string | US |
| `from` | date | 2026-01-27 |
| `to` | date | 2026-04-27 |

> **(*) Required** | Max 90-day date range

---

### Response

```json
[
	{
		"date": "2026-04-08 23:50:00",
		"country": "JP",
		"event": "Foreign Bond Investment (Apr/04)",
		"currency": "JPY",
		"previous": -945.4,
		"estimate": null,
		"actual": -2462.4,
		"change": -1516.9,
		"impact": "Low",
		"changePercentage": -160.434,
		"unit": null
	}
]

```