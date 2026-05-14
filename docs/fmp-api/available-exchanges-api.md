## Available Exchanges API

Access a complete list of supported stock exchanges using the FMP Available Exchanges API. This API provides a comprehensive overview of global stock exchanges, allowing users to identify where securities are traded and filter data by specific exchanges for further analysis.

### About Available Exchanges API

The FMP Available Exchanges API offers users a detailed listing of all supported stock exchanges, providing valuable information for investors, traders, and researchers who want to understand where securities are traded. Key features include:

* **Global Exchange List:** Retrieve a complete list of supported exchanges from around the world, including major stock exchanges such as NYSE, NASDAQ, and more.
* **Exchange Name and Short Name:** Get both the full exchange name and the short code for easy identification and filtering.
* **Data Filtering by Exchange:** Use this list to filter further queries based on specific exchanges, ensuring focused and accurate data retrieval for your needs.

This API is essential for those looking to organize or filter financial data based on stock exchange information.

---

### Example Use Case

A financial analyst can use the Available Exchanges API to create a customized dashboard that filters stock price data by different exchanges, ensuring they track securities relevant to specific markets.

---

### Endpoint

`https://financialmodelingprep.com/stable/available-exchanges`

---

### Response

```json
[
	{
		"exchange": "AMEX",
		"name": "New York Stock Exchange Arca",
		"countryName": "United States of America",
		"countryCode": "US",
		"symbolSuffix": "N/A",
		"delay": "Real-time"
	}
]

```