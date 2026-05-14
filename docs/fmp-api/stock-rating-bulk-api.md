## Stock Rating Bulk API

The FMP Rating Bulk API provides users with comprehensive rating data for multiple stocks in a single request. Retrieve key financial ratings and recommendations such as overall ratings, DCF recommendations, and more for multiple companies at once.

### About Stock Rating Bulk API

The FMP Rating Bulk API offers detailed rating information for stocks across global exchanges. This API is useful for:

* **Accessing Comprehensive Ratings:** Receive ratings based on multiple financial indicators like DCF, ROE, ROA, and PE ratios.
* **Bulk Data Requests:** Retrieve rating data for multiple stocks in a single API call, making data retrieval more efficient.
* **Supporting Investment Decisions:** Use the rating data to help guide buy, hold, or sell decisions for individual or bulk stocks based on comprehensive financial analysis.

This API is valuable for investors, financial analysts, and developers looking to integrate bulk rating data into their platforms or reports.

---

### Endpoint

`https://financialmodelingprep.com/stable/rating-bulk`

---

### Response

```json
[
	{
		"symbol": "000001.SZ",
		"date": "2025-07-09",
		"rating": "B+",
		"discountedCashFlowScore": "5",
		"returnOnEquityScore": "3",
		"returnOnAssetsScore": "2",
		"debtToEquityScore": "1",
		"priceToEarningsScore": "4",
		"priceToBookScore": "4"
	}
]

```