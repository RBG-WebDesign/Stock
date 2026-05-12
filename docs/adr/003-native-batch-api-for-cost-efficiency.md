# ADR 003: Native Provider Batch APIs for Cost Efficiency

**Date:** 2026-05-12
**Status:** Accepted

## Context
While OpenRouter is excellent for rapid model swapping and synchronous testing, the primary goal of this project is to scale to 1,000+ tickers daily. At this volume, synchronous API calls are cost-prohibitive and prone to timeout issues. Native providers (OpenAI and Anthropic) offer "Batch APIs" that process requests asynchronously within 24 hours at a 50% discount.

## Decision
We will use native Anthropic and OpenAI SDKs/APIs for the production screening pipeline to leverage Batch API pricing. OpenRouter will be retained solely for Phase 1 development, prompt debugging, and ad-hoc single-ticker analysis.

## Consequences
* **Positive:** 50% reduction in LLM operational costs. Higher reliability for high-volume processing.
* **Negative:** Requires managing multiple API keys (Anthropic/OpenAI) and implementing separate polling/retrieval logic for each provider's batch system.