# Current State

Status: Active
Last updated: 2026-07-16
Owner: Tech Lead

## Product And Code

- the product is edit-first with explicit `Edit Photo` and `Create from Scratch` modes
- base and optional reference-image roles are explicit
- portrait presets, generated-image-to-edit handoff, before/after compare, history, download, and reuse exist
- pending-review outputs require explicit reveal before normal reuse
- the frontend is componentized but `frontend/app/chat/page.tsx` still owns substantial API, persistence, and
  EventSource orchestration
- backend jobs, runs, and images persist in SQLite plus filesystem storage
- runner abstractions cover Qwen T2I, Qwen Edit, FLUX GGUF, and SDXL OpenVINO lanes

## Verified Reliability Baseline

- backend startup and fast-check API smoke pass on the current workstation
- frontend lint, typecheck, and production build have passed in the current workspace
- non-model backend tests cover pending-review reveal, API reveal responses, pending-output cleanup, model
  registration, seed behavior, startup, and queued/running restart classification
- scratch-copy validation proved reveal promotes a pending output to `output_image_id`, clears
  `pending_output_image_id`, changes the job to `succeeded`, and makes the run reusable
- the live WR3-007 pending-review fixture remains intentionally unrevealed
- one approved FLUX CPU draft edit completed in 2387 seconds and reached `pending_review`
- the 2026-07-16 frontend lint, typecheck, and production build rerun passed in 77 seconds
- the same host release-smoke rerun correctly stopped at backend startup because the fallback Python environment
  lacks Pillow; this confirms exit propagation but is not clean-install evidence

Historical Sprint 2 and Sprint 3 evidence lives in:

- `docs/planning/sprint-2-closeout-audit.md`
- `docs/planning/sprint-3-closeout-audit.md`

## Active Strategy

- CPU-only operation is a hard roadmap constraint
- there is no current GPU purchase or hosted-GPU plan
- Windows Sandbox is the preferred clean-Windows surrogate
- Docker/WSL2 is a reproducibility lane, not native Windows acceptance evidence
- local SQLite orchestration remains the default product path
- Temporal is an optional non-model learning path after the local orchestration contract exists
- Saga compensation applies only to partial side effects
- model changes require benchmark evidence

Decision sources:

- `docs/planning/strategy-checkpoint.md`
- `docs/adr/0005-cpu-first-product-and-validation-strategy.md`
- `docs/adr/0006-durable-job-orchestration.md`

## Current Sprint

Sprint 4 remains active as a beta-preparation and evidence sprint.

Complete or prepared:

- draft-lane beta scope is locked
- off-box Qwen acceptance packet is prepared
- current-workstation non-model release smoke passed
- installation guide, operator packet, result log, tester handoff, session runbook, and risk register exist
- Windows Sandbox clean-export, dependency-install, smoke, and evidence harness is implemented
- immutable `e829507` Sandbox package and signed installer manifest are prepared
- tester copy is owner-reviewed

Pending:

- isolated clean-Windows installation and non-model smoke
- result entry in `docs/testing/target-clean-machine-smoke-result-log.md`
- first controlled tester session, if still desired after the isolated smoke

Because no separate fresh machine exists, Windows Sandbox surrogate evidence is now acceptable for Sprint 4
closure when it is labeled honestly. Independent physical-machine evidence remains a residual risk.

## Planned Sprint

Sprint 5 is planned in `docs/planning/sprint-5-outline.md`:

1. isolated Windows smoke harness
2. reproducible Python and Docker dependency baseline
3. automated frontend flow tests
4. EventSource transport reconciliation
5. durable attempts and orchestration boundary
6. cancellation, bounded retry, and restart recovery
7. CPU and UI performance baseline
8. optional Temporal non-model spike
9. later model candidate review

## Current Blockers And Risks

| Risk | State | Next action |
| --- | --- | --- |
| No isolated clean-Windows result | Host Sandbox app blocker | Reset Sandbox through Windows Settings and retry the prepared `e829507` package once. |
| Sandbox app 0.8.107.0 misses `WinRT.Runtime 2.2.0.0` | Reproduced after host restart and Repair | Keep tester handoff blocked unless the owner explicitly accepts this residual risk. |
| Current host Python environment cannot rerun backend smoke | Open, environment-specific | Install dependencies only in Sandbox and use that result as the clean proof. |
| Local Qwen Edit native crash | Open, off-box | Do not force local acceptance; keep packet ready. |
| Frontend has no automated flow suite | Open | Add Playwright in Sprint 5. |
| EventSource transport loss can be confused with job failure | Open | Separate transport and job errors, then reconcile through the API. |
| Queued/running work is failed on restart | Known limitation | Add attempts, leases, and explicit recovery policy. |
| Python dependencies are not reproducibly pinned | Open | Add reviewed constraints/lock and pin Diffusers revision. |
| Next.js 14 is outside current support | Open | Protect flows first, then upgrade incrementally. |
| No independent physical tester machine | Accepted residual risk | Retain honest environment labels and revisit later. |

## Immediate Next Action

Use Windows Settings to reset the Windows Sandbox system component, retry the existing `e829507` package once, and
record the real result before deciding whether to accept the blocker or reinstall the optional feature. Do not begin
runtime orchestration changes or tester handoff yet.

## Heavy-Run Rule

Do not submit an edit job or run Qwen, FLUX, conversion, or other heavy model work without explicit user approval
after stating expected CPU, memory, and time cost.
