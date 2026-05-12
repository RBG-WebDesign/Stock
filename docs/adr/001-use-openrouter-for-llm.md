# ADR 001: Use OpenRouter for LLM Access

**Date:** 2026-05-12
**Status:** Accepted

## Context
The pipeline requires a highly capable Vision LLM to read complex chart setups and output strictly structured JSON. We need the ability to test different models (e.g., Claude 3.5 Sonnet vs. GPT-4o) to find the best balance of pattern recognition accuracy and cost per token. Managing separate SDKs (OpenAI, Anthropic, Google) is tedious and clutters the codebase.

## Decision
We will use OpenRouter as our unified API gateway for all LLM calls. 

## Consequences
* **Positive:** We can swap models instantly by changing a single string in `.env`. We only need to write one API interface in our code. We maintain a single billing dashboard.
* **Negative:** Introduces a third-party middleman, which could theoretically add slight latency or experience downtime independent of the core model providers.