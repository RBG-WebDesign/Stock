# FMP Articles API

Access the latest articles from Financial Modeling Prep with the **FMP Articles API**. Get comprehensive updates including headlines, snippets, and publication URLs to stay informed on the latest market trends.

---

## About FMP Articles API

The FMP Articles API provides access to a curated list of the most recent articles published by Financial Modeling Prep. This endpoint offers:

* **Headlines:** Stay informed with the latest headlines covering a wide range of financial topics.
* **Snippets:** Quickly grasp the key points of each article with concise content snippets.
* **Publication URLs:** Access the full articles through provided URLs for in-depth reading.

This API is updated regularly to ensure you have access to the most current content, helping you stay informed about the latest trends, insights, and analyses from Financial Modeling Prep.

**Endpoint:**

```http
https://financialmodelingprep.com/stable/fmp-articles?page=0&limit=20

```

---

## FMP Articles API Parameters

| Query Parameter | Type | Example | Description |
| --- | --- | --- | --- |
| `page` | number | 0 | The page number for pagination. |
| `limit` | number | 20 | The number of articles to return per page. |

**Notes:**

* `*` indicates a **Required** parameter (None are strictly required for this endpoint, though defaults apply).

---

## Example Response

```json
[
  {
    "title": "Merck Shares Plunge 8% as Weak Guidance Overshadows Strong Revenue Growth",
    "date": "2025-02-04 09:33:00",
    "content": "<p><a href='https://financialmodelingprep.com/financial-summary/MRK'>Merck & Co (NYSE:MRK)</a> saw its stock sink over 8% in pre-market today after delivering mixed fourth-quarter results...</p>",
    "tickers": "NYSE:MRK",
    "image": "https://cdn.financialmodelingprep.com/images/fmp-1738679603793.jpg",
    "link": "https://financialmodelingprep.com/market-news/fmp-merck-shares-plunge-8-as-weak-guidance-overshadows-strong-revenue-growth",
    "author": "Davit Kirakosyan",
    "site": "Financial Modeling Prep"
  }
]

```