## Company Profile Bulk API

The FMP Profile Bulk API allows users to retrieve comprehensive company profile data in bulk. Access essential information, such as company details, stock price, market cap, sector, industry, and more for multiple companies in a single request.

### About Company Profile Bulk API

The FMP Profile Bulk API provides detailed profiles of companies across global stock exchanges. This API is ideal for users who need to:

* **Retrieve Comprehensive Data:** Access company profiles that include stock prices, market capitalization, industry classification, and more.
* **Bulk Data Requests:** Get company details for multiple organizations in one API call, making data collection more efficient.
* **Analyze Company Information:** Use this data to gain insights into company operations, leadership, financials, and industry sectors.

This API is highly beneficial for financial analysts, data scientists, and anyone needing extensive company profile data for various organizations.

---

### Endpoint

`https://financialmodelingprep.com/stable/profile-bulk?part=0`

---

### Company Profile Bulk API Parameters

| Query Parameter | Type | Example |
| --- | --- | --- |
| `part*` | string | 0 |

> **(*) Required**

---

### Response

```json
[
	{
		"symbol": "AAPL",
		"price": 271.36,
		"marketCap": 4009711150080,
		"beta": 1.107,
		"lastDividend": 1.03,
		"range": "169.21-288.62",
		"change": -0.83,
		"changePercentage": -0.30493,
		"volume": 44494594,
		"averageVolume": 48811139,
		"companyName": "Apple Inc.",
		"currency": "USD",
		"cik": "0000320193",
		"isin": "US0378331005",
		"cusip": "037833100",
		"exchangeFullName": "NASDAQ Global Select",
		"exchange": "NASDAQ",
		"industry": "Consumer Electronics",
		"website": "https://www.apple.com",
		"description": "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide. The company offers iPhone, a line of smartphones; Mac, a line of personal computers; iPad, a line of multi-purpose tablets; and wearables, home, and accessories comprising AirPods, Apple TV, Apple Watch, Beats products, and HomePod. It also provides AppleCare support and cloud services; and operates various platforms, including the App Store that allow customers to discover and download applications and digital content, such as books, music, video, games, and podcasts, as well as advertising services include third-party licensing arrangements and its own advertising platforms. In addition, the company offers various subscription-based services, such as Apple Arcade, a game subscription service; Apple Fitness+, a personalized fitness service; Apple Music, which offers users a curated listening experience with on-demand radio stations; Apple News+, a subscription news and magazine service; Apple TV+, which offers exclusive original content; Apple Card, a co-branded credit card; and Apple Pay, a cashless payment service, as well as licenses its intellectual property. The company serves consumers, and small and mid-sized businesses; and the education, enterprise, and government markets. It distributes third-party applications for its products through the App Store. The company also sells its products through its retail and online stores, and direct sales force; and third-party cellular network carriers, wholesalers, retailers, and resellers. Apple Inc. was founded in 1976 and is headquartered in Cupertino, California.",
		"ceo": "Timothy D. Cook",
		"sector": "Technology",
		"country": "US",
		"fullTimeEmployees": "164000",
		"phone": "(408) 996-1010",
		"address": "One Apple Park Way",
		"city": "Cupertino",
		"state": "CA",
		"zip": "95014",
		"image": "https://images.financialmodelingprep.com/symbol/AAPL.png",
		"ipoDate": "1980-12-12",
		"defaultImage": false,
		"isEtf": false,
		"isActivelyTrading": true,
		"isAdr": false,
		"isFund": false
	}
]

```