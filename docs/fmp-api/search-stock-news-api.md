# Search Stock News API

Search for stock-related news using the **FMP Search Stock News API**. Find specific stock news by entering a ticker symbol or company name to track the latest developments.

---

### About Search Stock News API

The Search Stock News API helps users find stock-related news by entering a specific company name or stock symbol. This tool is ideal for:

* **Targeted News Searches:** Narrow down your search to find news about specific companies or stocks.
* **Symbol-Based Lookup:** Quickly retrieve news by entering the relevant ticker symbol for a stock.
* **Comprehensive News Retrieval:** Access both current and historical news reports to gain a full picture of stock movements over time.

This API is tailored for investors and analysts who require fast, reliable access to news affecting specific stocks.

> **Example Use Case:** A trader uses the Search Stock News API to look up recent news articles about a stock they are considering buying, helping them make an informed decision.

---

### API Details

**Endpoint:**
`https://financialmodelingprep.com/stable/news/stock?symbols=AAPL`

#### Parameters

| Query Parameter | Type | Example | Description |
| --- | --- | --- | --- |
| **symbols*** | string | `AAPL` | The ticker symbol(s) to search for. |
| **from** | date | `2026-01-27` | The start date for the news search. |
| **to** | date | `2026-04-28` | The end date for the news search. |
| **page** | number | `0` | The page number for pagination. |
| **limit** | number | `20` | Number of results per request (Max 250). |

** Required | Page limit: 100*

---

### Response Format

```json
[
  {
    "symbol": "AAPL",
    "publishedDate": "2025-02-03 21:05:14",
    "publisher": "Zacks Investment Research",
    "title": "Apple & China Tariffs: A Closer Look",
    "image": "https://images.financialmodelingprep.com/news/apple-china-tariffs-a-closer-look-20250203.jpg",
    "site": "zacks.com",
    "text": "Tariffs have been the talk of the town over recent weeks, regularly overshadowing other important developments and causing volatility spikes.",
    "url": "https://www.zacks.com/stock/news/2408814/apple-china-tariffs-a-closer-look?cid=CS-STOCKNEWSAPI-FT-stocks_in_the_news-2408814"
  }
]

```