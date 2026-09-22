# Sprint 5 Outline

Status: Planned; starts after Sprint 4 isolated clean-environment evidence is recorded
Sprint name: Sprint 5 - CPU Reliability, Reproducibility, And Durable Workflows
Duration: 2 to 3 weeks
Last updated: 2026-07-16
Parent strategy: `docs/planning/strategy-checkpoint.md`
Decision inputs:

- `docs/adr/0005-cpu-first-product-and-validation-strategy.md`
- `docs/adr/0006-durable-job-orchestration.md`
- `docs/planning/sprint-4-release-checklist-and-risk-register.md`

Sprint owner: Tech Lead

## 1. Goal

Make the existing CPU-first edit workflow reproducible, testable, cancellable, retryable, and honest across
browser disconnects and backend restarts without adding a GPU dependency or a new editing surface.

## 2. Entry Gate

Sprint 5 starts after one of these is recorded:

- Windows Sandbox clean-environment release smoke passes, or
- Windows Sandbox is unavailable and Sprint 4 records an owner-accepted blocker plus residual risk

No model run is needed for the entry gate.

## 3. In Scope

- Windows Sandbox clean-smoke harness and evidence
- repeatable Docker/WSL2 non-model smoke lane
- pinned Python dependency baseline
- automated frontend product-flow tests
- SSE disconnect and job-status reconciliation
- durable job attempts, leases, cancellation, retry, and restart recovery
- CPU performance and UI responsiveness measurements
- optional non-model Temporal learning spike
- documentation and architecture consistency

## 4. Out Of Scope

- requiring or purchasing a GPU
- hosted inference
- new engine families
- masking, region editing, batch editing, or mobile
- automatic retry of deterministic model crashes
- claims of mid-step diffusion resume
- model replacement without benchmark evidence

## 5. Workstreams And Tickets

### WR5-001 - Isolated Windows release smoke

- Priority: P0
- Owner: DevOps + Release Guard
- Work: export a clean commit, launch Windows Sandbox, install dependencies inside it, run
  `scripts/release_smoke.ps1`, and record the environment honestly
- Progress: harness implemented; host Sandbox app crashes before bootstrap (`WinRT.Runtime 2.2.0.0`).
  Owner accepted this as residual risk on 2026-09-22. It is not a gate for Sprint 5 backend work.
  Do not claim a clean-machine smoke pass.
- Done when: residual acceptance is recorded (this note) or a future machine actually passes smoke

### WR5-002 - Reproducible dependency baseline

- Priority: P0
- Owner: Backend + DevOps
- Work: replace open-ended Python dependency resolution with a reviewed lock/constraints strategy; pin the
  Diffusers source revision; add `.dockerignore` and a non-model Docker smoke path
- Done when: two clean installs resolve the same direct dependency baseline and smoke passes without model assets

### WR5-003 - Frontend flow-test foundation

- Priority: P0
- Owner: Frontend + UX Reviewer
- Work: add Playwright coverage using a deterministic non-model backend fixture or API interception
- Required flows: edit mode, base/reference roles, job progress, pending review, reveal, compare, download/reuse,
  retry command, and transport disconnect recovery
- Progress (2026-09-22): `npm run test:e2e` covers edit mode, one-image vs two-image roles, progress,
  pending review + reveal, compare/download/reuse, same-job retry, and stream-disconnect reconciliation.
- Done when: primary flows pass from one documented command and failure traces are retained

### WR5-004 - Job stream reconciliation

- Priority: P0
- Owner: Frontend + Backend
- Work: separate server job-error events from EventSource transport errors; on disconnect, query persisted job
  state and reconnect with bounded backoff
- Progress (2026-09-22): Done in PR #6 — `/chat` reconciles via `GET /api/jobs/{id}` and reconnects with
  exponential backoff; messages effect cannot bypass reconnect ownership
- Done when: a transient stream disconnect cannot mark an active or completed job failed without backend evidence

### WR5-005 - Durable attempt schema and orchestration boundary

- Priority: P0
- Owner: Backend Architect
- Work: introduce `JobOrchestrator`, `AttemptExecutor`, immutable retry inputs, attempt records, normalized failure
  classes, leases, and heartbeats
- Done when: local SQLite orchestration preserves attempt history and existing API behavior remains compatible
- Progress (2026-09-22): `job_attempts` plus `app/orchestration.py` record begin/heartbeat/finish.
  Restart still marks queued/running jobs failed (WR5-007) but closes the open attempt as `process_restart`.

### WR5-006 - Cancellation and bounded retry

- Priority: P0
- Owner: Backend + Frontend
- Work: add persisted cancel request, cooperative Diffusers cancellation, child-process termination for `sd-cli`,
  manual retry, and one-retry transient policy
- Progress (2026-09-22): persisted `cancel_requested`, cooperative step cancel, `sd-cli` child
  termination, one automatic retry for worker-dispatch failures, and same-job manual retry.
- Done when: non-model fakes prove graceful cancel, forced child termination, retryable failure, and no-retry failure

### WR5-007 - Restart recovery

- Priority: P0
- Owner: Backend + Reviewer
- Work: requeue persisted queued/retry-wait work, classify expired running leases as interrupted, preserve terminal
  states, and make retry policy explicit
- Done when: restart tests prove state transitions without launching a model

### WR5-008 - CPU and UI performance baseline

- Priority: P1
- Owner: Performance Engineer + Frontend
- Work: record queue wait, model-load time, execution time, peak RAM, progress-event rate, and output-commit time;
  reduce synchronous timeline persistence and unnecessary progress rerenders
- Done when: a report compares baseline and changed behavior using non-model fakes plus existing approved evidence

### WR5-009 - Temporal durable-execution spike

- Priority: P1
- Owner: Backend Architect
- Work: optional local Temporal dev-server experiment using fake long-running activities only
- Required proofs: heartbeat, cancel, retry, worker restart, service restart, pending-review signal, idempotent output
  commit, and comparison with `LocalSqliteOrchestrator`
- Done when: an ADR follow-up records adopt, defer, or reject; Temporal remains optional until then

### WR5-010 - Model candidate review

- Priority: P2
- Owner: AI/ML + Product
- Work: define benchmark thresholds before considering a FLUX variant, quantized Qwen path, or another candidate
- Progress (2026-09-22): `Qwen-Image-2.1` (+ community GGUF) catalogued as frontier successor *candidate*
  in `docs/models/model-catalog.md`; not registered; not a CPU-mainline replacement for OpenVINO
- Done when: a decision packet exists; any actual model execution remains separately approval-gated

## 6. Execution Order

1. WR5-001 isolated Windows smoke
2. WR5-002 reproducible dependencies
3. WR5-003 frontend flow-test foundation
4. WR5-004 stream reconciliation
5. WR5-005 durable attempt boundary
6. WR5-006 cancellation and retry
7. WR5-007 restart recovery
8. WR5-008 performance baseline
9. WR5-009 optional Temporal spike
10. WR5-010 model candidate review

WR5-003 and WR5-004 may overlap after the deterministic frontend test fixture exists. Durable schema changes must
land before cancellation, retry, and recovery behavior.

## 7. Verification Ladder

Every implementation slice should prefer:

1. unit/state-machine tests
2. API tests against temporary SQLite databases
3. Playwright tests against deterministic non-model states
4. Windows Sandbox and Docker release smoke
5. approval-gated model run only when behavior cannot be established otherwise

## 8. Exit Criteria

- clean isolated non-model setup evidence is recorded
- Python dependencies are reproducible enough for repeatable clean installs
- primary frontend workflows have automated browser coverage
- stream disconnect is not confused with job failure
- cancellation, manual retry, and restart recovery have cheap deterministic tests
- attempts and failure classes are durable and inspectable
- CPU performance fields and baseline are documented
- Temporal has an evidence-based adopt/defer/reject result if the optional spike is run
- no local GPU dependency was introduced

## 9. Risks

| Risk | Mitigation |
| --- | --- |
| Durable-workflow work becomes a framework rewrite | Keep API and runners stable; build the local contract first. |
| Retry duplicates expensive work or outputs | Use attempt ids, idempotent commit, and a one-retry default. |
| Cancellation corrupts native state | Isolate non-cooperative runtimes in child processes and clean temporary artifacts. |
| Temporal distracts the product | Keep it optional, non-model, and time-boxed. |
| Docker evidence is mistaken for Windows support | Label it reproducibility evidence only. |
| CPU performance work lowers output quality | Keep smoke/draft/acceptance evidence separate. |

## 10. First Implementation Slice

Implement WR5-001 after the documentation checkpoint:

- add a Windows Sandbox configuration and bootstrap script
- export a clean source package from the approved commit
- run only installation and `scripts/release_smoke.ps1`
- record the result without running a model
