# Backend Architecture

Status: Active
Last updated: 2026-07-16
Owner: Backend Architect

## Current Modules

- `backend/app/main.py`: FastAPI routes, startup, status, job, run, image, export, and cleanup surfaces
- `backend/app/jobs.py`: queue submission, local worker loop, execution lifecycle, persistence updates, SSE events,
  reveal, deletion, and restart classification
- `backend/app/db.py`: SQLite connection and schema initialization
- `backend/app/images.py`: image persistence and metadata
- `backend/app/status_copy.py`: API presentation metadata for machine states
- `backend/inference/*`: runner contract and model-specific execution
- `backend/worker/main.py`: optional remote/local HTTP worker and callback relay

## API Ownership

The backend owns:

- machine-readable job and run state
- immutable-enough request snapshots for replay/retry
- image and output metadata
- runner capability and asset validation
- readiness and system information
- reveal and reuse gates
- future cancellation, retry, attempt, lease, and recovery semantics

The backend does not own product wording, top-level information architecture, or preset marketing language.

## Current Execution

Local mode uses an in-memory queue and daemon worker threads. Runners cache loaded pipelines in process. Worker
mode persists the job then dispatches its id over HTTP; the worker calls back with events.

Startup recovery currently marks queued and running jobs `failed` with `server restarted`. This is metadata-safe
but not durable execution.

## Current Strengths

- startup and fast-check API smoke are working
- job/run/image persistence is established
- runner capabilities are normalized
- progress and activity fields survive EventSource reconnection
- pending-review reveal has transactional state checks and cheap regression tests
- local and worker modes share one API contract

## Current Risks

- queue ownership is in process memory
- no persisted attempt, worker lease, or heartbeat contract exists
- no durable cancel or retry command exists
- native work may run inside a process that cannot be stopped safely
- automatic retry could duplicate expensive work without idempotent commit
- direct inference routes bypass the queued lifecycle and should not expand
- dependency versions are not reproducibly pinned

## Target Boundaries

### JobOrchestrator

Owns submit, cancel, retry, recovery, policy, and state transitions.

### AttemptExecutor

Owns one invocation, progress heartbeat, cancellation cooperation, temporary output, failure normalization, and
atomic result commit.

### Runner

Owns model loading, capability, parameter translation, and model-specific execution. It does not decide retry or
job-level recovery policy.

### Event Publisher

Publishes presentation-independent state changes. Transport loss must not mutate persisted job outcome.

## Default And Experimental Orchestration

- default: SQLite-backed local orchestrator
- experimental: Temporal adapter using the same orchestration contract

Temporal is deferred by ADR 0007. Do not add it as a release dependency.

## Safety Rules

- use one heavy local model at a time
- run non-cooperative native inference in a child process before promising cancellation
- cap automatic retries at one by default
- never auto-retry invalid input, missing assets, OOM, deterministic native crash, or user cancellation
- do not claim mid-step resume without real runner checkpoints
