# Fast-Check Runbook

## Purpose

`fast-check` exists to keep CPU-only development practical without lowering the final quality bar.

## Profiles

- backend: `backend/.env.fast-check`
- frontend: `frontend/.env.fast-check`

## Startup commands

Backend main mode:
`.\scripts\start_backend.ps1 -Mode main`

Backend fast-check mode:
`.\scripts\start_backend.ps1 -Mode fast-check`

Frontend:
`cd frontend && npm run dev`

Frontend note:
Next.js does not auto-load `frontend/.env.fast-check`. The current fast-check frontend expectation is the normal local dev server, because the backend URL remains `http://localhost:8000`.

Backend smoke check:
`.\scripts\smoke_backend.ps1`

## Current backend fast-check defaults

- local inference mode
- separate SQLite database
- `cpu-low` profile
- `512x512`
- `8` default steps
- `12` step ceiling
- one active engine at a time

## Standard Sprint 1 smoke engine

- engine: `qwen-image-2512`
- command: `.\scripts\smoke_qwen_t2i.ps1`
- reason:
  - already scoped in `backend/.env.fast-check`
  - uses the canonical mirrored-asset path
  - exercises the current T2I queue path without requiring upload/edit setup first

## When to use fast-check

- frontend integration work
- API and queue validation
- job-event and SSE checks
- preset and prompt direction checks
- replay/history flow checks

## When not to use fast-check

- final quality decisions
- milestone sign-off
- release candidate approval

## Recommended ladder

### Smoke

- `384-512px`
- `4-8` steps
- purpose: correctness

### Draft

- `512px`
- `8-12` steps
- purpose: product iteration

### Acceptance

- `768px`
- `16-24` steps on the main Qwen lane
- purpose: quality validation

The durable ladder contract lives in `docs/workflows/preset-ladder.md`.

## Operational note

The fast-check profile is a developer productivity tool. It is not a substitute for acceptance validation.

## Validated Sprint 1 baseline

- backend loads with `DOTENV_PATH=backend/.env.fast-check`
- database resolves to `data/app.fast-check.db`
- `/health` returns `200`
- `/api/models` returns `200`
- fast-check currently scopes to one active model: `qwen-image-2512`
- standard inference smoke command: `.\scripts\smoke_qwen_t2i.ps1`
