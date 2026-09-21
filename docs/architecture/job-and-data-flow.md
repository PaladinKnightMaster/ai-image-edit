# Job And Data Flow

Status: Active; target orchestration states are planned
Last updated: 2026-07-16
Owner: Backend Architect

## Current Entities

- `jobs`: top-level lifecycle and progress
- `runs`: model, prompt, inputs, parameters, output ids, and latency
- `images`: uploaded and generated image metadata
- filesystem: image bytes and engine-specific temporary output

## Current States

```text
queued -> running -> succeeded
                  -> pending_review -> succeeded after reveal
                  -> failed
```

On backend restart, persisted queued and running jobs are marked failed. Pending-review and terminal jobs remain
stable.

## Current Edit Flow

1. frontend uploads or reuses base and optional reference image ids
2. frontend submits `/api/jobs/edit`
3. backend validates runner capability, assets, inputs, and limits
4. backend inserts job and run rows
5. local queue or worker executes the runner
6. backend persists progress and emits SSE events
7. output is committed as visible or pending review
8. reveal promotes `pending_output_image_id` to `output_image_id`
9. succeeded outputs become available for compare, download, and reuse

## Target Entities

Add `job_attempts` so retry and recovery do not overwrite execution history. The target record contains attempt
number, worker, lease, heartbeat, timings, exit status, failure class, retryability, and temporary/committed output
references.

## Target State Model

```text
queued -> running -> pending_review -> succeeded
              |             |
              |             -> cancelled
              -> cancel_requested -> cancelled
              -> interrupted -> retry_wait -> queued
              -> failed
```

These states are introduced incrementally with migrations and contract tests.

## Cancellation Flow

1. client requests cancellation
2. orchestrator persists `cancel_requested`
3. attempt executor signals a cooperative runner or terminates its child process
4. executor removes only uncommitted temporary artifacts
5. orchestrator records `cancelled`
6. API publishes the persisted outcome

Closing the browser or losing EventSource does not cancel a job.

## Retry Flow

1. failure is normalized
2. policy classifies retryable or terminal
3. automatic retry is capped at one by default
4. a retry creates a new attempt with the same request snapshot
5. output commit uses attempt identity to prevent duplicate publication

Manual retry remains available for eligible failed/interrupted jobs. Deterministic native crashes, invalid input,
missing assets, OOM, and cancellation do not auto-retry.

## Restart Recovery

- `queued` and `retry_wait` may be re-enqueued
- expired running leases become `interrupted`
- interrupted work may restart from step 1 when policy allows
- no mid-step diffusion resume is promised
- terminal and pending-review states survive unchanged

## Saga Compensation

Compensation may remove orphaned temporary output, clear uncommitted references, release leases, and reverse a
partial metadata write. It must not delete user uploads or previously committed successful outputs.

## Temporal Learning Flow

The optional Temporal adapter first models a fake attempt Activity. It uses heartbeat, cancellation, retry,
worker/service restart, a review signal, and idempotent result commit. Image bytes remain in the filesystem; only
small identifiers and metadata belong in workflow history.
