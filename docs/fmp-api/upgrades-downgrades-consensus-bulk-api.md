## Upgrades Downgrades Consensus Bulk API

The Upgrades Downgrades Consensus Bulk API provides a comprehensive view of analyst ratings across all symbols. Retrieve bulk data for analyst upgrades, downgrades, and consensus recommendations to gain insights into the market's outlook on individual stocks.

### About Upgrades Downgrades Consensus Bulk API

This API allows users to access:

* **Analyst Recommendations:** Get detailed ratings such as strong buy, buy, hold, sell, and strong sell for multiple stocks in a single request.
* **Consensus Ratings:** View the overall consensus for each stock based on analyst recommendations, helping you assess the general market sentiment.
* **Upgrades and Downgrades Trends:** Track recent upgrades or downgrades across different symbols to identify potential investment opportunities or risks.
* **Market Insights:** Gain valuable insights into how the market views a stock’s future performance, based on expert analysis and recommendations.

This API is particularly useful for institutional investors, portfolio managers, and financial analysts who want to monitor stock ratings in bulk, helping them make more informed decisions based on the latest market trends and analyst opinions.

---

### Endpoint

`https://financialmodelingprep.com/stable/upgrades-downgrades-consensus-bulk`

---

### Response

```json
[
	{
		"symbol": "AAPL",
		"strongBuy": "0",
		"buy": "1",
		"hold": "1",
		"sell": "0",
		"strongSell": "0",
		"consensus": "Buy"
	}
]

```