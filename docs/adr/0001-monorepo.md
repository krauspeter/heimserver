# 0001 – One monorepo for the whole system

- **Status:** accepted
- **Date:** 2026-11-11

## Context

The system consists of several parts: infrastructure (Docker Compose, backups), a Modbus collector,
a backend with a rule engine, a mobile app and an ML forecast. They are developed by one person and
deployed together onto one mini PC.

## Options

1. **One repo per component** – clean separation, independent versioning; but cross-cutting
   changes need several PRs, and the overall system is hard to see.
2. **Monorepo** – everything in one place, one CI, one `docker compose up`; needs a clear folder
   structure and per-folder CI jobs as it grows.

## Decision

We use a **monorepo**. The whole system is visible in one place, a change that touches collector
and backend is one commit, and moving to new hardware stays a single `docker compose up`.

## Consequences

- Each component gets its own folder with its own `pyproject.toml` (or app tooling).
- CI jobs are split per component and later filtered by changed paths.
- Shared tool configuration (ruff, mypy) lives in the root `pyproject.toml`.
