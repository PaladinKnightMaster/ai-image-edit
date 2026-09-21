# Backend Architecture

## Scope

This document describes the current backend implementation, not the ideal future state.

## Main modules

- `backend/app/main.py`
  - FastAPI app
  - readiness, health, version, models, system, job, image, stats, replay, export endpoints
- `backend/app/jobs.py`
  - job queue submission
  - local worker loop
  - SSE event publication
  - run persistence and job lifecycle
- `backend/worker/main.py`
  - worker-mode HTTP listener
  - queue dispatch from API to worker
  - callback-based event relay to the API
- `backend/app/db.py`
  - SQLite connection and schema init
- `backend/app/images.py`
  - image persistence and metadata
- `backend/inference/*`
  - model runner abstraction and concrete runtime lanes

## API surface

The backend exposes four main surfaces:

1. platform status
   - `/health`
   - `/ready`
   - `/api/version`
   - `/api/system`
   - `/api/models`
   - `/api/stats`

2. queued job workflow
   - `/api/jobs/t2i`
   - `/api/jobs/edit`
   - `/api/jobs/{job_id}`
   - `/api/jobs/{job_id}/events`
   - `/api/jobs/{job_id}/reveal`

3. direct inference workflow
   - `/api/infer/t2i`
   - `/api/infer/edit`

4. image and run management
   - `/api/images/upload`
   - `/api/images/{image_id}`
   - `/api/images/{image_id}/meta`
   - `/api/runs`
   - `/api/runs/{run_id}`
   - export, replay, delete, cleanup endpoints

## Execution model

### Local mode

- jobs are queued in process memory
- worker threads run inside the API process
- simplest local setup

### Worker mode

- API persists job metadata in SQLite
- API dispatches `job_id` to the worker over HTTP
- worker calls back into the API with event payloads
- result lifecycle remains API-owned

## Strengths

- The API contract is already broad enough for a real product.
- Runner isolation is clean enough to support multiple runtime lanes.
- SSE progress is already present.
- Manual reveal support exists for lanes that require review gating.

## Risks

- Startup is currently blocked by `backend/app/config.py`.
- Queue durability is weak because in-memory job execution is lost on restart.
- Worker mode still depends on callback availability and short HTTP hops.
- The model lifecycle is not centralized in one authoritative catalog.

## What this backend should own

- API contract stability
- job lifecycle and recovery semantics
- storage conventions
- runner loading and capability checks
- system and readiness reporting

## What it should not own

- product copy and UI mode selection
- preset wording
- top-level information architecture
