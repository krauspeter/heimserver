# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project

Home server (Beelink EQ14, Debian, Docker) with a family notification app, Sungrow PV integration
via Modbus TCP and, later, a weather-based ML forecast. See `README.md` and `docs/adr/`.

The author is an experienced embedded developer (C/C++) learning Python backends, app development
and ML. Explain new concepts briefly in German so he can explain them himself in interviews.

## Layout

Follow the structure in `README.md` (`infra/`, `collector/`, `backend/rules/`, `app/`, `ml/`).
One module per rule in `backend/rules/`.

## Commands
  Windows + Git Bash. Activate venv first: source .venv/Scripts/activate

```bash
pip install -e "collector[dev]"
ruff check . && ruff format --check .
mypy collector/src
pytest
```

## Rules

- Small steps, each with tests. CI must stay green.
- Type hints everywhere (`mypy --strict`).
- Never commit secrets; config via `.env`, document new keys in `.env.example`.
- Inverter access is **read-only** unless explicitly decided otherwise in an ADR.
- Commit messages: Conventional Commits (`feat:`, `fix:`, `docs:`, `ci:`, `chore:`, `test:`).
