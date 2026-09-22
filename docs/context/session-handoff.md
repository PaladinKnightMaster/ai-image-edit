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
- Sprint 4: open residual — Windows Sandbox host blocker (`WinRT.Runtime`) still unresolved; product work
  continued without claiming clean-machine smoke pass
- OpenVINO mainline: shipped (PRs #3–#5) — SDXL OpenVINO is primary local t2i + edit; hardware advisor in UI
- Sprint 5: **active focus** — Backend + UI reliability (stream reconciliation → durable jobs → cancel/retry)

## Locked Decisions

- no local GPU or hosted-GPU dependency is planned
- **local mainline model: `sdxl-openvino`** (t2i + edit)
- FLUX GGUF remains optional slow advanced draft
- Qwen 2512 / Edit 2511 remain GPU / off-box frontier (not daily driver)
- **Qwen-Image-2.1** is a catalogued frontier *candidate* only — no download/runner until gated evaluation
- Windows Sandbox remains the preferred clean-Windows surrogate when the host feature works
- local SQLite orchestration remains the default
- Temporal is optional and must start as a non-model learning spike
- all heavy model runs require explicit approval

Decision sources:

- `docs/planning/strategy-checkpoint.md`
- `docs/adr/0005-cpu-first-product-and-validation-strategy.md`
- `docs/adr/0006-durable-job-orchestration.md`
- `docs/models/model-catalog.md`

## Current Evidence

- SDXL OpenVINO edit verified in-app (~37s Natural Skin Retouch from library base on i7-14700 CPU)
- Hardware fit panel live via `GET /api/hardware` (PR #5)
- one approved FLUX CPU edit reached `pending_review` in 2387 seconds (historical)
- Windows Sandbox app still crashes before bootstrap (`WinRT.Runtime 2.2.0.0`); no clean-machine pass recorded
- local Qwen Edit remains blocked / off-box

## Immediate Next Action

Execute Sprint 5 Backend + UI reliability in strategy order, starting with:

1. **WR5-004** — SSE / job-stream reconciliation (do not treat transport disconnect as job failure)
2. then WR5-003 Playwright flow foundation (may overlap)
3. then WR5-005 → WR5-006 → WR5-007 durable attempts, cancel/retry, restart recovery
4. WR5-002 dependency pinning and WR5-001 Sandbox disposition remain open parallel tracks

## Then

- WR5-008 performance / UI responsiveness (includes OpenVINO img2img progress denominator polish)
- WR5-010 evaluate Qwen-Image-2.1 only on GPU/off-box with fixtures — never as CPU mainline replacement

## Key Risks

- do not claim independent-machine compatibility from Sandbox or Docker
- do not confuse EventSource disconnection with backend job failure
- do not promise mid-step diffusion resume
- do not download Qwen-Image-2.1 onto the CPU box as a product default
- do not automatically retry deterministic native crashes or out-of-memory failures

## Bootstrap Order

Read `AGENTS.md`, core/war-room docs, this handoff, `docs/context/current-state.md`,
`docs/planning/strategy-checkpoint.md`, and `docs/planning/sprint-5-outline.md`.
