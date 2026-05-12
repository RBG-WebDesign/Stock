# Company Share Float & Liquidity API

Understand the liquidity and volatility of a stock with the **FMP Company Share Float and Liquidity API**. Access the total number of publicly traded shares for any company to make informed investment decisions.

---

## About Company Share Float & Liquidity API

The FMP Company Share Float and Liquidity API provides essential data on the number of publicly traded shares for a given company—commonly referred to as the **float**. This endpoint helps investors:

* **Evaluate Stock Liquidity:** Identify the number of shares available for trading, which directly impacts the liquidity of the stock.
* **Assess Volatility:** Understand how the size of a company’s float can influence price movements. Smaller floats generally lead to higher volatility.
* **Make Informed Decisions:** Use float data to identify companies with large or small floats, helping to assess the potential risk and reward of specific positions.

Generally, companies with a **large float** tend to have more liquid stocks and less price volatility, while companies with a **small float** may experience higher price fluctuations due to lower liquidity.

**Endpoint:**

```http
https://financialmodelingprep.com/stable/shares-float?symbol=AAPL

```

---

## Company Share Float & Liquidity API Parameters

| Query Parameter | Type | Example | Description |
| --- | --- | --- | --- |
| `symbol`* | string | AAPL | The stock ticker symbol. |

**Notes:**

* `*` indicates a **Required** parameter.

---

## Example Response

```json
[
  {
    "symbol": "AAPL",
    "date": "2026-04-07 07:43:00",
    "freeFloat": 99.77245934530808,
    "floatShares": 14664480994,
    "outstandingShares": 14697924749,
    "source": "https://www.sec.gov/Archives/edgar/data/320193/000032019326000006/aapl-20251227.htm"
  }
]

```