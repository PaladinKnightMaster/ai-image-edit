# Current State

Status: Active
Last updated: 2026-09-22
Owner: Tech Lead

## Product And Code

- the product is edit-first with explicit `Edit Photo` and `Create from Scratch` modes
- base and optional reference-image roles are explicit
- portrait presets, generated-image-to-edit handoff, before/after compare, history, download, and reuse exist
- pending-review outputs require explicit reveal before normal reuse
- `/chat` sidebar includes a **Hardware fit** panel backed by `GET /api/hardware`
- the frontend is componentized but `frontend/app/chat/page.tsx` still owns substantial API, persistence, and
  EventSource orchestration (stream disconnect reconciles via the job API)
- backend jobs, runs, and images persist in SQLite plus filesystem storage
- runner abstractions cover Qwen T2I, Qwen Edit, FLUX GGUF, and SDXL OpenVINO lanes

## Runtime Lanes (truth)

| Lane | Role | Hardware |
| --- | --- | --- |
| `sdxl-openvino` | **Primary local** t2i + img2img edit | CPU / Intel OpenVINO |
| `flux2-klein-9b-gguf` | Optional slow advanced draft | CPU (very slow) / GPU faster |
| `qwen-image-2512` / `qwen-image-edit-2511` | Frontier off-box | CUDA GPU |
| Qwen-Image-2.1 | Catalogued candidate only | Evaluate off-box later; not a CPU mainline replacement |

## Verified Reliability Baseline

- OpenVINO SDXL edit smoke on this workstation (~37s library-base Natural Skin Retouch)
- OpenVINO txt2img and edit unit tests exist; hardware advisor endpoint tests exist
- backend startup and fast-check API smoke pass on the current workstation (project `.venv`)
- frontend lint, typecheck, and production build have passed in the current workspace
- non-model backend tests cover pending-review reveal, API reveal responses, pending-output cleanup, model
  registration, seed behavior, startup, and queued/running restart classification
- scratch-copy validation proved reveal promotes a pending output to `output_image_id`, clears
  `pending_output_image_id`, changes the job to `succeeded`, and makes the run reusable
- the live WR3-007 pending-review fixture remains intentionally unrevealed unless an owner changes that decision
- one approved FLUX CPU draft edit completed historically in 2387 seconds and reached `pending_review`
- Windows Sandbox clean-machine smoke is **not** recorded (host `WinRT.Runtime 2.2.0.0` crash; reproduced after
  restart, Repair, and Reset)

Historical Sprint 2 and Sprint 3 evidence lives in:

- `docs/planning/sprint-2-closeout-audit.md`
- `docs/planning/sprint-3-closeout-audit.md`

## Active Strategy

Locked constraints (see `docs/planning/strategy-checkpoint.md` and ADRs 0005/0006):

- CPU-only operation is a hard roadmap constraint; no GPU purchase or hosted-GPU plan
- **local mainline:** `sdxl-openvino` (t2i + edit) — 2026-09 amendment over the older FLUX-as-draft default
- Windows Sandbox is the preferred clean-Windows surrogate when the host feature works
- Docker/WSL2 is a reproducibility lane, not native Windows acceptance evidence
- local SQLite orchestration remains the default product path
- Temporal is an optional non-model learning path after the local orchestration contract exists
- Saga compensation applies only to partial side effects
- model changes require benchmark evidence; Qwen-Image-2.1 is candidate-only until then

## Sprint Status

### Sprint 4 — residual open (beta / clean-env evidence)

Complete or prepared (still true):

- draft-lane beta scope is locked; off-box Qwen acceptance packet is prepared
- installation guide, operator packet, result log, tester handoff, session runbook, and risk register exist
- Windows Sandbox clean-export, dependency-install, smoke, and evidence harness is implemented
- immutable `e829507` Sandbox package and signed installer manifest are prepared
- tester copy is owner-reviewed

Still pending:

- isolated clean-Windows installation and non-model smoke result
- owner disposition on the persistent Sandbox host blocker (accept residual risk vs optional-feature reinstall)
- first controlled tester session, if still desired after the isolated smoke

Product work (OpenVINO mainline, hardware UI) continued without claiming a clean-machine smoke pass.
Independent physical-machine evidence remains an accepted residual risk.

### Sprint 5 — active Backend + UI reliability track

Roadmap in `docs/planning/sprint-5-outline.md` (strategy quality order unchanged):

| ID | Work | Status |
| --- | --- | --- |
| WR5-001 | Isolated Windows smoke / owner blocker disposition | Accepted residual (2026-09-22): Sandbox host stays broken; not a Sprint 5 gate |
| WR5-002 | Reproducible Python / Docker dependency baseline | Done — constraints + Diffusers SHA + Docker non-model smoke |
| WR5-003 | Playwright frontend flow-test foundation | Done (mocked flows: roles, progress, reveal, compare, retry, reconnect) |
| WR5-004 | EventSource / job-stream reconciliation | Done (PR #6) |
| WR5-005 | Durable attempt schema / orchestration boundary | Done (PR #8) |
| WR5-006 | Cancellation and bounded retry | Done (PR #9) |
| WR5-007 | Restart recovery | Done (PR #11) |
| WR5-008 | CPU and UI performance baseline | Done — see `docs/planning/cpu-ui-performance-baseline.md` |
| WR5-009 | Optional Temporal spike | Not started |
| WR5-010 | Model candidate review (incl. Qwen-Image-2.1) | Candidate noted only |

**Backend + UI improvement strategy is not complete.** OpenVINO + hardware UI closed a product/runtime gap;
they do not close Sprint 5 reliability tickets.

## Current Blockers And Risks

| Risk | State | Next action |
| --- | --- | --- |
| No isolated clean-Windows result | Accepted residual | Sandbox host crash is not a gate. Do not claim clean-machine compatibility. |
| Sandbox app 0.8.107.0 misses `WinRT.Runtime 2.2.0.0` | Accepted residual | Harness stays in repo. Revisit only on another Windows machine. |
| Local Qwen Edit native crash / GPU requirement | Open, off-box | Do not force local acceptance; keep packet ready; 2.1 is candidate only. |
| Frontend flow coverage is partial | Closed for primary mocked flows | Extend only if a new product path lands. |
| EventSource transport loss confused with job failure | Mitigated (PR #6) | Keep covered by Playwright reconnect cases in WR5-003. |
| Queued/running work is failed on restart | Mitigated | Queued work is requeued. A running attempt retries once, then fails. |
| Python dependencies are not reproducibly pinned | Mitigated | WR5-002: constraints + Diffusers SHA + Docker non-model smoke. |
| Next.js 14 is outside current support | Mitigated | Upgraded to Next.js 15.5.25 + React 19 (incremental; 16 deferred). |
| No independent physical tester machine | Accepted residual risk | Retain honest environment labels. |

## Immediate Next Action

1. Optional WR5-009 Temporal spike, or WR5-010 gated Qwen-Image-2.1 evaluation off-box only.
2. Next.js 16 remains a later increment. Do not treat Windows Sandbox as a gate. Do not download Qwen-Image-2.1 onto this CPU box as a product default.

## Heavy-Run Rule

Do not submit an edit job or run Qwen, FLUX, conversion, or other heavy model work without explicit user approval
after stating expected CPU, memory, and time cost.
