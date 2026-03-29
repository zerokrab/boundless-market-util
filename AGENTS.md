# AGENTS.md — boundless-market-util

AI coding assistant instructions for this repository.

## Purpose

`market_util.py` is a **single-file** Python CLI script. Keep it that way — no packages, no external dependencies, no setup.py. `curl` is the only allowed external tool (beyond Python stdlib).

## Key conventions

- **No dependencies** — Python stdlib + `curl` subprocess only.
- **Logs to stderr**, table to stdout — preserve this separation.
- **`curl_get()`** is the sole network function — all HTTP calls go through it.
- Cycle values come from the Boundless Explorer API: `total_cycles` (prover) and `work_submitted` (miner).
- Epoch range is user-supplied and inclusive on both ends.

## API endpoints used

| Purpose | Endpoint |
|---------|----------|
| Prover market data | `GET /api/provers/{address}/aggregates/epoch` |
| Miner PoVW data | `GET /api/miners/{address}/aggregates/epoch` |

Base URL: `https://explorer.boundless.network/api`

## PR workflow

- Branch naming: `zeroklaw/<description>`
- Always open PRs — no direct pushes to `main`.
- Git identity: `name = zeroklaw`, `email = 267418690+zeroklaw@users.noreply.github.com`.
