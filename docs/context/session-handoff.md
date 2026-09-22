# Session Handoff

Status: Active
Last updated: 2026-09-22
Owner: War Room Center / Commander

## Recovered Objective

Build a local, offline-after-setup, edit-first AI image application that remains fully developable on the current
CPU-only Windows desktop. Improve workflow quality, reliability, reproducibility, and performance before
considering model replacement.

## Current Phase

- Sprint 3: closed
- Sprint 4: residual accepted — Windows Sandbox host blocker is not a Sprint 5 gate; no clean-machine pass claimed
- Sprint 5: **active** — P0s closed; Next.js 15.5.25 + React 19 landed (PR #14); Next 16 deferred

## Locked Decisions

- no local GPU or hosted-GPU dependency is planned
- **local mainline model: `sdxl-openvino`** (t2i + edit)
- FLUX GGUF remains optional slow advanced draft (historical draft evidence; not the daily default)
- Qwen 2512 / Edit 2511 remain GPU / off-box frontier (not daily driver)
- **Qwen-Image-2.1** is a catalogued frontier *candidate* only — no download/runner until gated evaluation
- Windows Sandbox remains the preferred clean-Windows surrogate when the host feature works
- Docker/WSL2 is for repeatable non-model validation, not Windows acceptance
- local SQLite orchestration remains the default
- Temporal is optional and must start as a non-model learning spike
- Saga compensation is limited to partial side effects
- browser Service Workers do not own inference or durable jobs
- all heavy model runs require explicit approval

Decision sources:

- `docs/planning/strategy-checkpoint.md`
- `docs/adr/0005-cpu-first-product-and-validation-strategy.md`
- `docs/adr/0006-durable-job-orchestration.md`
- `docs/models/model-catalog.md`

## Current Evidence

- SDXL OpenVINO edit verified in-app (~37s Natural Skin Retouch from library base on i7-14700 CPU)
- Hardware fit panel live via `GET /api/hardware` (PR #5)
- non-model reveal/reuse and restart-classification tests exist; WR3-007 pending fixture remains unrevealed
- one approved FLUX CPU edit reached `pending_review` in 2387 seconds (historical)
- Windows Sandbox clean-export / `e829507` package prepared; app still crashes before bootstrap
  (`WinRT.Runtime 2.2.0.0`; restarted / Repair / Reset retries failed identically)
- clean isolated Windows result is not recorded
- local Qwen Edit remains blocked / off-box
- Sprint 5 landed: WR5-003–008 (Playwright flows, SSE reconcile, attempts, cancel/retry, restart recovery,
  CPU/UI baseline). WR5-002 verified: pinned Diffusers SHA, `backend/constraints.txt`, two matching resolves,
  Docker non-model `/health` + startup unittest.

## Immediate Next Action

1. Optional WR5-009 Temporal spike, or WR5-010 gated Qwen-Image-2.1 eval off-box only
2. Or Next.js 16 as a later increment when ready
3. Do not treat Windows Sandbox as a gate and do not download Qwen-Image-2.1 as the CPU default

## Then

- optional WR5-009 Temporal spike
- WR5-010 evaluate Qwen-Image-2.1 only off-box/GPU with fixtures — never as CPU mainline replacement

## Key Risks

- do not claim independent-machine compatibility from Sandbox or Docker
- do not confuse EventSource disconnection with backend job failure
- do not promise mid-step diffusion resume
- do not download Qwen-Image-2.1 onto the CPU box as a product default
- do not automatically retry deterministic native crashes or out-of-memory failures
- preserve the live WR3-007 pending fixture unless its decision changes explicitly

## Bootstrap Order

Read `AGENTS.md`, core/war-room docs, this handoff, `docs/context/current-state.md`,
`docs/planning/strategy-checkpoint.md`, Sprint 4 residual notes in current-state, and
`docs/planning/sprint-5-outline.md`.
