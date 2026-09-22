# ADR 0006: Durable Job Orchestration

- Status: Accepted
- Date: 2026-07-16
- Owners: Backend Architect + Tech Lead
- Temporal follow-up: deferred by `docs/adr/0007-defer-temporal.md` (2026-09-22)

## Context

Image inference is a long-running, side-effecting operation. The current local queue runs in process memory,
and startup recovery marks queued and running jobs failed. The frontend consumes SSE progress but currently
mixes transport disconnection with job failure behavior.

The project needs cancellation, deliberate retry, restart recovery, and trustworthy manual review. Temporal
and Saga patterns are relevant, but the default product is a single-user, single-machine, offline-first app.
A required Temporal service would add packaging and operational cost before the local execution contract is
stable.

## Decision

Introduce an orchestration boundary while keeping SQLite as the default durable control plane.

```text
Job API
  -> JobOrchestrator
      -> LocalSqliteOrchestrator      default product path
      -> TemporalOrchestrator         optional learning path
  -> AttemptExecutor
  -> Existing model Runner
```

The API contract and runner abstraction remain stable. Orchestration decides when an attempt starts, retries,
cancels, or recovers. The attempt executor owns one model invocation and its temporary artifacts.

## Target State Model

```text
queued -> running -> pending_review -> succeeded
              |             |
              |             -> cancelled
              -> cancel_requested -> cancelled
              -> interrupted -> retry_wait -> queued
              -> failed
```

The implementation may introduce states incrementally. API consumers must branch on machine-readable state,
not presentation copy.

## Attempt Model

Add an append-oriented `job_attempts` record with at least:

- attempt id, job id, and attempt number
- worker id and execution mode
- lease expiry and last heartbeat
- start and finish timestamps
- exit code and normalized failure type
- retryable flag
- temporary and committed output identifiers

Job request snapshots remain immutable enough to reproduce a manual retry with the same model, prompt, inputs,
seed, and parameters.

## Cancellation

- cancellation is a persisted request, not only a browser action
- Diffusers runners should check cancellation through their per-step callback
- `sd-cli` and non-cooperative native runtimes should run in a child process that can be terminated
- a job becomes `cancelled` only after the executor stops and cleanup completes
- browser disconnect never means job cancellation

## Retry

Automatic retry is limited to transient failures such as a lost worker lease or recoverable process launch
failure. Missing assets, invalid input, out-of-memory, deterministic native crashes, and user cancellation are
not automatically retried.

CPU inference is expensive, so the default automatic retry budget is one retry. Manual retry creates a new
attempt and preserves the original history.

## Restart Recovery

- persisted `queued` and `retry_wait` work can be re-enqueued
- a `running` attempt with an expired lease becomes `interrupted`
- interrupted work may retry from the beginning when policy allows
- diffusion computation is not claimed to resume mid-step unless a future runner supplies real checkpoints
- `pending_review`, `succeeded`, `failed`, and `cancelled` remain stable across restart

## Saga Use

Use Saga-style compensation only for partial side effects:

- remove orphaned temporary outputs
- clear uncommitted output references
- release attempt leases
- roll back metadata that did not reach atomic output commit

Never compensate by deleting user uploads or previously committed successful outputs. Reveal is a business
transition, not a compensation step.

## Temporal Policy

Temporal is an optional, non-model learning lane after the local orchestration contract exists. The first spike
must use a fake long-running activity and prove heartbeat, cancellation, retry, worker restart, service restart,
manual-review signal, and idempotent output commit.

Temporal must not become the default runtime until it demonstrates enough value to justify an additional local
service and packaging dependency.

ADR 0007 defers that spike. The local contract already covers the proofs, so Temporal is not installed.

## Frontend And Service Worker Boundary

The frontend owns connection state, progress presentation, and user commands. It must reconcile SSE transport
loss with `GET /api/jobs/{id}` before declaring failure.

A browser Service Worker may later cache static shell assets, but it does not own model execution, durable job
state, cancellation, retry, or restart recovery.

## Consequences

- reliability can improve without replacing the runner architecture
- cancellation becomes feasible for native work through process isolation
- retries become explicit, bounded, and observable
- the project gains practical durable-execution experience without forcing Temporal into the product path
- schema, process supervision, and failure classification require careful tests before model execution uses them
