# Job Status And Recovery States

Status: Active; Sprint 5 extensions are planned
Last updated: 2026-07-16
Owner: Backend + Frontend
Decision: `docs/adr/0006-durable-job-orchestration.md`

## Purpose

Define machine-readable job states, user meaning, recovery behavior, and the boundary between implemented and
planned states.

## Implemented States

| State | User meaning | Terminal | Reusable |
| --- | --- | --- | --- |
| `queued` | Waiting for the local execution slot | No | No |
| `running` | Local inference is active | No | No |
| `pending_review` | Output exists but requires explicit reveal | Stable review gate | No |
| `succeeded` | Output is committed and available | Yes | Yes |
| `failed` | Backend recorded terminal failure | Yes | No |

API clients branch on `status`. Presentation fields such as `status_label`, `status_detail`, `stage_label`, and
`error_detail` are copy helpers only.

## Implemented Reveal Transition

```text
pending_review
  -> copy pending_output_image_id to output_image_id
  -> clear pending_output_image_id
  -> set job status succeeded
  -> publish status and result events
  -> expose output to history and reuse
```

This transition has temporary-database, API, scratch-copy, and browser evidence. The live WR3-007 fixture remains
pending intentionally.

## Current Restart Behavior

On backend initialization:

- persisted `queued` becomes `failed`
- persisted `running` becomes `failed`
- error is `server restarted`
- `pending_review`, `succeeded`, and existing `failed` jobs remain stable

This behavior is safe for metadata consistency but loses queued work and cannot retry interrupted work.

## Planned Sprint 5 States

These states are not yet implemented and must not be exposed as working product behavior before migrations and
tests land:

| State | Meaning |
| --- | --- |
| `cancel_requested` | Persisted cancellation command; executor shutdown pending |
| `cancelled` | Executor stopped and temporary cleanup completed |
| `interrupted` | Running attempt lost its worker or lease |
| `retry_wait` | Retryable work recorded and waiting for policy/backoff |

## Planned Recovery Policy

| Pre-restart state | Target recovery |
| --- | --- |
| `queued` | Re-enqueue when request snapshot and policy are valid |
| `running` with expired lease | Mark attempt interrupted, then retry or stop by policy |
| `retry_wait` | Re-enqueue after backoff/policy check |
| `cancel_requested` | Ensure executor is absent, clean temporary output, finalize cancelled |
| `pending_review` | Preserve unchanged |
| terminal | Preserve unchanged |

Restart recovery means workflow/attempt recovery, not mid-step diffusion resume.

## Failure Classification

Retryable examples:

- expired worker lease
- transient child-process launch failure
- temporary database or filesystem contention

Non-retryable examples:

- invalid input
- missing or incompatible model assets
- unsupported runner capability
- out-of-memory
- deterministic native crash
- user cancellation

Automatic retry is capped at one by default. Manual retry creates a new attempt.

## Transport Boundary

EventSource transport loss is not a job state. The frontend must show reconnecting, fetch
`GET /api/jobs/{job_id}`, render persisted state, and reconnect only for non-terminal jobs. A job becomes failed
only when the backend reports `failed`.

## Observer Timeout Boundary

A benchmark observer timeout means the wrapper stopped waiting. It must not mark the backend job failed. The job
may continue and later reach pending review, success, or failure.

## Cancellation Boundary

Closing the browser does not cancel inference. Cancellation becomes real only after the backend persists the
request and the attempt executor stops cooperatively or terminates its child process.

## Required Tests

- every allowed transition and rejected transition
- reveal atomicity and reuse visibility
- idempotent output commit
- transient versus deterministic retry classification
- cancel request and cleanup
- restart recovery by persisted state and lease
- EventSource disconnect reconciliation
- pending-review stability across restart
