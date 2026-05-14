## Company Profile Data API

Access detailed company profile data with the **FMP Company Profile Data API**. This API provides key financial and operational information for a specific stock symbol, including market capitalization, stock price, industry, and more.

---

### About Company Profile Data API

The FMP Company Profile Data API offers comprehensive insights into a company's financial status and operational details. It is designed for analysts, traders, and investors who require an in-depth look at core financial metrics and business information.

**Key Features:**

* **Stock Price and Market Cap:** Retrieve the latest stock price and market capitalization.
* **Company Details:** Access company name, description, CEO, and industry classification.
* **Financial Metrics:** Track dividend yield, stock beta, and trading ranges to assess performance and volatility.
* **Global Identifiers:** Retrieve identifiers like **CIK**, **ISIN**, and **CUSIP** for accurate cross-platform tracking.
* **Contact Information:** Obtain the company’s address, phone number, and website.
* **IPO Data:** View the company's IPO date, sector, and active trading status.

---

### Example Use Case

An investor researching tech investments can use this API to review the financial health of **Apple Inc. (AAPL)**, evaluating performance metrics like stock range and market cap to inform trading decisions.

**Endpoint:**
`https://financialmodelingprep.com/stable/profile?symbol=AAPL`

---

### API Parameters

| Query Parameter | Type | Example | Description |
| --- | --- | --- | --- |
| **symbol*** | string | `AAPL` | The stock ticker symbol for the company. |

*(*) Required*

---

### Response Example

```json
[
  {
    "symbol": "AAPL",
    "price": 262.82,
    "marketCap": 3900351299800,
    "beta": 1.109,
    "lastDividend": 1.04,
    "range": "169.21-265.29",
    "change": 3.24,
    "changePercentage": 1.24817,
    "volume": 36725325,
    "averageVolume": 47424558,
    "companyName": "Apple Inc.",
    "currency": "USD",
    "cik": "0000320193",
    "isin": "US0378331005",
    "cusip": "037833100",
    "exchangeFullName": "NASDAQ Global Select",
    "exchange": "NASDAQ",
    "industry": "Consumer Electronics",
    "website": "https://www.apple.com",
    "description": "Apple Inc. designs, manufactures, and markets smartphones...",
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