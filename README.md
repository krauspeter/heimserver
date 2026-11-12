# heimserver

> Home energy assistant: a small always-on server that collects PV data, sends notifications to the family's phones and — later — uses a weather-based ML forecast to tell us *when* to run the big appliances.

[![CI](https://github.com/krauspeter/heimserver/actions/workflows/ci.yml/badge.svg)](https://github.com/krauspeter/heimserver/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)

**Status:** 🚧 Phase 0 – project setup (Nov 2026)

---

## The problem

We have a PV system with battery storage at home. Most of the surplus energy is fed into the grid at a low tariff, because nobody knows the right moment to start the washing machine, the dishwasher or the dryer. On top of that, everyday reminders (waste collection, frost, storms) get lost.

**Goal:** one system that knows the house — and tells the family at the right time.

## Features (planned)

| Feature | Phase | Status |
|---|---|---|
| Always-on home server (mini PC, Docker, backups, remote access via Tailscale) | 1 | ⏳ |
| PV raw data logger (Sungrow inverter, Modbus TCP, every 30–60 s) | 1 | ⏳ |
| Family app with push notifications (waste collection, frost/rain/storm) | 2 | ⏳ |
| Grafana dashboard: production, consumption, battery, feed-in | 3 | ⏳ |
| PV surplus notifications with thresholds and quiet hours | 3 | ⏳ |
| ML forecast from weather data → "Tomorrow from 11 am the washing machine pays off" | 4 | ⏳ |

## Architecture

<!-- TODO: replace with an exported diagram (docs/architecture.png) -->

```
 Sungrow inverter ──Modbus TCP──► collector ──► database ◄── Grafana
                                                  │
 weather API / waste iCal ─────────────► backend (FastAPI, rule engine)
                                                  │ push
                                                  ▼
                                         family phones (app)

 Ryzen PC (wakes via Wake-on-LAN) ── trains forecast ──► backend
```

- **Mini PC** (Beelink EQ14, Debian, Docker) runs 24/7: collects data, evaluates rules, sends notifications.
- **Ryzen PC** only wakes up for ML training and hands the forecast back to the mini PC.

Design decisions are documented as [Architecture Decision Records](docs/adr/).

## Repository layout

```
heimserver/
├── docs/            decisions (ADRs), requirements, operations
├── infra/           docker-compose.yml, backup scripts
├── collector/       Modbus collector for Sungrow (Python)
├── backend/         FastAPI, rule engine, push delivery
│   └── rules/       one module per rule: muell, wetter, pv_ueberschuss
├── app/             PWA or Flutter app
├── ml/              forecast: notebooks, training, evaluation
└── .github/workflows/  CI: lint, type check, tests
```

## Quick start

> Will be filled in with Phase 1. Target: three commands.

```bash
git clone https://github.com/krauspeter/heimserver.git
cd heimserver && cp .env.example .env
docker compose -f infra/docker-compose.yml up -d
```

## Development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e "collector[dev]"
ruff check . && ruff format --check . && mypy collector/src && pytest
```

## Measurements

Honest numbers will go here: server power draw, forecast accuracy, kWh shifted into self-consumption.

## Safety

- Read-only access to the inverter first; write commands only once registers and consequences are understood.
- No open ports to the internet — remote access via Tailscale only.
- No secrets in the repo: credentials live in `.env` (git-ignored); only `.env.example` is committed.

## About

Built by Peter Kraus — embedded software engineer (C/C++, 7 years automotive ECUs) expanding into Python backends, app development and machine learning.

## License

[MIT](LICENSE)
