# Test Strategy

## Goal

Keep the project testable on a CPU-only machine while preserving a real quality bar for the product.

## Current state

### Backend

- current automated tests are mostly inference-dependent
- there is no fast smoke suite for core API and queue behavior
- the current suite is too slow and environment-sensitive for day-to-day regression safety

### Frontend

- `lint` exists
- `typecheck` exists
- `build` exists
- there is no automated frontend flow test suite yet
- most flow validation is currently manual

## Test pyramid for this repo

### 1. Smoke

Runs often.

Backend:
- import/app startup
- `/health`
- `/ready`
- `/api/models`
- worker auth path
- queue submission happy path with mocked or lightweight conditions
- standard Sprint 1 inference smoke via `.\scripts\smoke_qwen_t2i.ps1`

Frontend:
- `npm run lint`
- `npm run build`
- later: explicit `tsc --noEmit`

### 2. Draft

Runs during feature work.

- fast-check inference on one active model
- history and replay flow
- upload and edit flow
- generated-image-to-edit flow

### 3. Acceptance

Runs at milestone gates.

- benchmark pack execution using `docs/testing/benchmark-pack.md`
- fixed-case manifest review via `docs/testing/benchmark-pack.v0.json`
- before/after product walkthrough
- manual visual review
- engine-specific validation for active MVP lanes

## CI recommendation

CI should focus on smoke-level checks:

- backend import
- backend static checks
- frontend lint
- frontend build
- selected API smoke tests

Do not make CI depend on full local inference or multi-hour CPU runs.

## Current gaps to close

- add backend smoke tests that do not require real model loading
- add lightweight benchmark execution notes on top of the benchmark pack v0
- separate smoke and acceptance responsibilities clearly in docs and scripts
