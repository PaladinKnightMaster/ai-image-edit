# Session Handoff

Status: Active
Last updated: 2026-07-16
Owner: War Room Center / Commander

## Recovered Objective

Build a local, offline-after-setup, edit-first AI image application that remains fully developable on the current
CPU-only Windows desktop. Improve workflow quality, reliability, reproducibility, and performance before
considering model replacement.

## Current Phase

- Sprint 3: closed
- Sprint 4: active until isolated clean-Windows smoke evidence or an owner-accepted blocker is recorded
- Sprint 5: planned as CPU reliability, reproducibility, and durable-workflow hardening

## Locked Decisions

- no local GPU or hosted-GPU dependency is planned
- Windows Sandbox is the clean-Windows surrogate because no fresh machine is available
- Docker/WSL2 is for repeatable non-model validation, not Windows acceptance
- local SQLite orchestration remains the default
- Temporal is optional and must start as a non-model learning spike
- Saga compensation is limited to partial side effects
- browser Service Workers do not own inference or durable jobs
- FLUX 9B remains local draft evidence; Qwen Edit acceptance remains off-box
- all heavy model runs require explicit approval

Decision sources:

- `docs/planning/strategy-checkpoint.md`
- `docs/adr/0005-cpu-first-product-and-validation-strategy.md`
- `docs/adr/0006-durable-job-orchestration.md`

## Current Evidence

- one approved FLUX CPU edit reached `pending_review` in 2387 seconds
- non-model reveal/reuse and restart-classification tests exist
- current-workstation backend smoke, frontend lint, typecheck, and build passed
- Windows Sandbox clean-export/install/evidence harness and immutable `e829507` package are prepared
- Sandbox app 0.8.107.0 crashes before bootstrap because `WinRT.Runtime 2.2.0.0` is missing; no mapped result exists
- the 2026-07-17 retry after host restart reproduced the identical crash
- current frontend lint, typecheck, and build pass; the fallback host Python correctly blocks backend smoke because
  Pillow is absent
- clean isolated Windows result is not yet recorded
- local Qwen Edit remains blocked by a reproducible native crash

## Immediate Next Action

Complete WR5-001 as the final Sprint 4 evidence slice:

1. use Windows Settings to repair the Windows Sandbox system component
2. retry `.artifacts/windows-sandbox-smoke/20260716T234119Z-e829507/ai-image-edit-smoke.wsb`
3. if the app starts, let the bootstrap install dependencies without copying `.venv` or `node_modules`
4. collect `sandbox-smoke-result.json`, `.txt`, and the transcript
5. if repair fails, reset Windows Sandbox and retry before accepting the blocker
6. record the environment as `Windows Sandbox surrogate`; do not run a model

Record the result in:

- `docs/testing/target-clean-machine-smoke-result-log.md`
- `docs/testing/clean-machine-release-smoke.md`
- `docs/planning/sprint-4-release-checklist-and-risk-register.md`

## Then

Start `docs/planning/sprint-5-outline.md` in order: reproducible dependencies, frontend flow tests, stream
reconciliation, durable attempts, cancellation/retry, restart recovery, performance baseline, and optional Temporal
spike.

## Key Risks

- do not claim independent-machine compatibility from Sandbox or Docker
- do not confuse EventSource disconnection with backend job failure
- do not promise mid-step diffusion resume
- do not automatically retry deterministic native crashes or out-of-memory failures
- preserve the live WR3-007 pending fixture unless its decision changes explicitly

## Bootstrap Order

Read `AGENTS.md`, core/war-room docs, this handoff, `docs/context/current-state.md`,
`docs/planning/strategy-checkpoint.md`, the active Sprint 4 outline, and the planned Sprint 5 outline.
