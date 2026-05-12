# ADR 005: uv for Dependency and Project Management

**Date:** 2026-05-12
**Status:** Accepted

## Context
Python dependency management is often slow and fragmented (pip, venv, poetry, etc.). We need a fast, reliable, and reproducible environment that is easy for both humans and AI agents to set up.

## Decision
We will use `uv` as the exclusive tool for project initialization, dependency management, and script execution (`uv run`).

## Consequences
* **Positive:** Near-instant dependency installation. Standardized `pyproject.toml` and `uv.lock` files ensure perfect environment replication. Simplifies documentation to a single `uv sync` command.
* **Negative:** Requires users to install the `uv` binary on their system.