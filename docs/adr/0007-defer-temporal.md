# ADR 0007: Defer Temporal; Keep SQLite Orchestration

- Status: Accepted
- Date: 2026-09-22
- Owners: Backend Architect + Tech Lead
- Follows: `docs/adr/0006-durable-job-orchestration.md`
- Closes: WR5-009

## Context

ADR 0006 kept SQLite as the product control plane and left Temporal as an optional non-model spike. The spike
was allowed only after the local contract existed, and only if it proved heartbeat, cancel, retry, restart,
a review signal, and idempotent commit on a fake activity.

That local contract is now implemented and tested:

- `job_attempts` record begin, heartbeat, and finish (WR5-005)
- persisted cancel plus one automatic retry for transient worker-dispatch failures (WR5-006)
- restart requeues queued work and retries a running attempt once from the start (WR5-007)
- pending review, reveal, and terminal states survive restart

The product is still one user, one machine, and offline after setup. An edit is one long runner invocation,
not a multi-service workflow. The project does not promise mid-step diffusion resume.

## Decision

**Defer Temporal.** Do not install a Temporal server, worker, or SDK for this product.

SQLite plus the existing attempt, cancel, retry, and restart policy remains the orchestration runtime.

Saga stays a local cleanup rule, not a workflow framework: remove orphan temporary outputs, clear uncommitted
output ids, and release attempt leases. Do not delete user uploads or already committed successful outputs.

## Options

| Option | Result |
| --- | --- |
| Adopt Temporal as the default orchestrator | Rejected. Adds a local service and packaging cost. It still restarts a diffusion step from the beginning. |
| Run the fake-activity spike now | Rejected for this pass. The proofs it would show are already covered by the SQLite tests. |
| Defer Temporal until a real multi-worker need appears | **Chosen.** |

## Revisit When

Open a new ADR before adopting Temporal. A valid reason is one of:

- more than one inference worker must share one durable queue
- a job is a real multi-step workflow across processes, not one runner call
- workflow history must outlive this app's SQLite file

A new model or a faster retry policy is not by itself a reason to adopt Temporal.

## Consequences

- WR5-009 is closed as deferred, not as an implementation spike
- no Temporal dependency enters install, Docker smoke, or release packaging
- retry behavior stays the current policy: one automatic retry for transient dispatch errors, manual retry
  otherwise, and one restart requeue for interrupted work
- compensation stays limited to partial side effects
