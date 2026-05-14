## Earnings Calendar API

Stay informed on upcoming and past earnings announcements with the FMP Earnings Calendar API. Access key data, including announcement dates, estimated earnings per share (EPS), and actual EPS for publicly traded companies.

### About Earnings Calendar API

The FMP Earnings Calendar API is an essential tool for investors, traders, and financial analysts who need to stay updated on the earnings announcements of publicly traded companies. This API is valuable for:

* **Tracking Earnings Announcements:** Access a comprehensive list of upcoming and past earnings announcements, including the date of the announcement, estimated EPS, and actual EPS (if available).
* **Informed Decision-Making:** Earnings announcements provide crucial insights into a company's financial performance and future outlook. Use this data to make informed trading and investment decisions.
* **Market Analysis:** Analyze the earnings performance of various companies over time to identify trends, compare performance across industries, and assess the potential impact on stock prices.

This API is a powerful resource for anyone who needs to monitor earnings announcements and use this information to guide their investment strategies.

---

### Example

**Trading Strategy:** A trader might use the Earnings Calendar API to track the earnings announcements of key technology companies. By knowing the estimated and actual EPS ahead of time, the trader can prepare to make informed trades based on how the market reacts to the earnings results.

**Endpoint:**
`https://financialmodelingprep.com/stable/earnings-calendar`

---

### Earnings Calendar API Parameters

| Query Parameter | Type | Example |
| --- | --- | --- |
| `from` | date | 2026-01-27 |
| `to` | date | 2026-04-27 |
| `page` | number | 0 |

> **(*) Required** | Maximum 4000 records per request | Max 90-day date range | Currency is as Trading

---

### Response

```json
[
  {
    "symbol": "KEC.NS",
    "date": "2024-11-04",
    "epsActual": 3.32,
    "epsEstimated": 4.97,
    "revenueActual": 51133100000,
    "revenueEstimated": 44687400000,
    "lastUpdated": "2024-12-08"
  }
]

```