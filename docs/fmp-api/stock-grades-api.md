# Stock Grades API

Access the latest stock grades from top analysts and financial institutions with the **FMP Grades API**. Track grading actions, such as upgrades, downgrades, or maintained ratings, for specific stock symbols, providing valuable insight into how experts evaluate companies over time.

---

## About Stock Grades API

The FMP Grades API offers timely data on stock evaluations by prominent financial institutions, including:

* **Grading Company:** Identify the institution providing the stock rating.
* **Previous Grade and New Grade:** View the change in grade, if any, from previous assessments to the latest one.
* **Action Taken:** Determine whether the grade was upgraded, downgraded, or maintained.
* **Date of Evaluation:** See when the latest grading action occurred.

This API helps investors and analysts understand the latest sentiment from financial experts, enabling better investment decisions based on how stocks are graded.

---

### Example Use Case

An investor can use the Grades API to track the latest stock ratings for their portfolio, seeing how financial institutions view the company's current performance and investment potential.

**Endpoint:**

```http
https://financialmodelingprep.com/stable/grades?symbol=AAPL

```

---

## Stock Grades API Parameters

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
    "date": "2025-01-31",
    "gradingCompany": "Morgan Stanley",
    "previousGrade": "Overweight",
    "newGrade": "Overweight",
    "action": "maintain"
  }
]

```