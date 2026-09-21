# Test Strategy

Status: Active
Last updated: 2026-07-16
Owner: Reviewer + Release Guard

## Goal

Keep daily validation fast on a CPU-only machine while preserving strong evidence for workflow correctness,
release reproducibility, and model quality.

## Current Coverage

Backend automated coverage includes:

- startup, `/health`, `/ready`, and `/api/models`
- model registration and runner-load behavior
- pending-review reveal and API response contracts
- reusable history after reveal
- pending-output cleanup on deletion
- queued/running restart classification
- seed determinism and FLUX adapter behavior

Frontend currently has:

- lint
- TypeScript typecheck
- production build
- manual browser evidence for reveal, reuse, download, and output-library flows

The primary current gap is automated frontend workflow coverage.

## Validation Layers

### 1. Static

Run on every frontend change:

- `npm.cmd run lint`
- `npm.cmd run typecheck`
- `npm.cmd run build`

### 2. Unit And State Machine

Use for:

- status transitions
- retry classification
- cancellation policy
- idempotent output commit
- frontend reducers, persistence, and transport reconciliation

No model may load.

### 3. API And Temporary Database

Use temporary SQLite databases and temporary image roots for:

- submit validation
- reveal and reuse
- delete and compensation
- attempts, leases, heartbeat, retry, and recovery
- cancel command lifecycle
- worker callback and auth behavior

### 4. Browser Flow

Use Playwright with deterministic backend states or API interception for:

- explicit edit/create mode
- base/reference input roles
- progress and disconnected/reconnecting state
- pending review and reveal
- compare, download, and reuse
- cancel and retry commands
- restart-recovery presentation

Browser tests must not submit a real model job.

### 5. Release Smoke

Run `scripts/release_smoke.ps1` on:

- current workstation
- Windows Sandbox clean-Windows surrogate
- Docker/WSL2 reproducibility lane after it exists

Record environment and commit. Do not flatten these evidence types into one compatibility claim.

### 6. Draft Model Evidence

Run only after explicit resource warning and approval. Record model, hardware, prompt/case, seed, parameters,
latency, peak RAM where available, output id, status, and review notes.

### 7. Acceptance Evidence

Use the fixed benchmark pack and review worksheet. Qwen acceptance may run off-box; it is separate from local
workflow and release-smoke evidence.

## Sprint 5 Required Tests

- EventSource disconnect reconciles through persisted job state
- server job error remains distinct from transport error
- cancel request reaches cooperative fake runner
- non-cooperative fake child process terminates and cleans temporary output
- transient failure retries once with a new attempt
- deterministic failure does not auto-retry
- restart requeues eligible work and interrupts expired running attempts
- pending-review remains stable across restart
- output commit is idempotent
- Windows Sandbox smoke records truthful environment metadata

## Test Data Policy

- use temporary databases for mutation tests
- preserve the live WR3-007 pending fixture
- avoid storing private source images in committed fixtures
- store model outputs only when they are intentional benchmark evidence
- keep model execution out of CI and default smoke

## Release Rule

A prepared script or packet is not evidence. A gate passes only when the exact command, environment, commit,
result, warnings, and blockers are recorded.

The Windows Sandbox harness has a cheap no-download contract check:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\scripts\windows-sandbox\test_harness_contract.ps1
```

It validates script syntax, pinned HTTPS prerequisite sources, signature requirements, package/hash guards,
native exit propagation, and absence of known model-execution entry points. It does not satisfy the isolated
Windows smoke gate by itself.
