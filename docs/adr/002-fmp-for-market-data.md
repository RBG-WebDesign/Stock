# ADR 002: FMP as Primary Fundamental Data Source

**Date:** 2026-05-12
**Status:** Accepted

## Context
To execute the CAN SLIM / Technofundamental strategy, we need robust historical and current fundamental data. Specifically, we require quarter-over-quarter EPS growth, gross margin expansion, and accurate market cap data. 

## Decision
We will use Financial Modeling Prep (FMP) as the primary data provider for fundamental metrics and the initial universe screening.

## Consequences
* **Positive:** FMP provides deep, institutional-grade fundamental data and income statements via a developer-friendly REST API. It is highly cost-effective compared to Bloomberg or FactSet.
* **Negative:** FMP's historical price data can sometimes be less precise on intra-day timeframes compared to dedicated tick-data providers.