# Project Strategy Checkpoint

Status: Locked
Date: 2026-07-16
Owners: War Room Center / Commander + Tech Lead
Decision ADRs:

- `docs/adr/0005-cpu-first-product-and-validation-strategy.md`
- `docs/adr/0006-durable-job-orchestration.md`

## Final Decision

AI Image Edit remains a local, offline-after-setup, edit-first product developed and operated on CPU-only
hardware. No GPU purchase, hosted GPU service, or local GPU dependency is part of the active roadmap.

The project will improve quality in this order:

1. reproducible clean-environment validation
2. automated product-flow coverage
3. trustworthy job transport and status reconciliation
4. durable attempts, cancellation, bounded retry, and restart recovery
5. CPU performance measurement and UI responsiveness
6. optional Temporal learning spike
7. benchmark-driven model evaluation

## Runtime Decision

- local default: SQLite-backed orchestration plus existing runner interfaces
- **local mainline (2026-09 amendment):** `sdxl-openvino` for both t2i and prompt-guided edit on CPU
- local optional slow draft: `flux2-klein-9b-gguf`
- intended frontier edit acceptance: `qwen-image-edit-2511` (and eventually Qwen-Image-2.1 if evidence
  supports replacement), off-box / GPU only
- Qwen-Image-2.1 is a catalogued candidate only — not downloaded, not registered, not a release dependency
- experimental orchestration: Temporal, non-model first and optional
- selective pattern: Saga compensation for partial side effects only

## Backend + UI Improvement Status (2026-09-22)

The quality order above is **not complete**. Completed adjacent product work (OpenVINO lane + hardware UI)
does not close Sprint 5 reliability tickets. Full ticket table lives in `docs/context/current-state.md`.

| Strategy step | Status |
| --- | --- |
| 1. Clean-environment validation | Open — Sandbox host blocker; no pass recorded (Sprint 4 residual) |
| 2. Automated product-flow coverage | Not started (WR5-003) |
| 3. Job transport / SSE reconciliation | In progress (WR5-004) |
| 4. Durable attempts / cancel / retry / restart | Not started (WR5-005–007) |
| 5. CPU + UI performance baseline | Not started (WR5-008); small OpenVINO progress polish in WR5-004 PR |
| 6. Optional Temporal spike | Not started |
| 7. Benchmark-driven model evaluation | Candidate noted only (WR5-010 / Qwen-Image-2.1) |

## Validation Decision

- Windows Sandbox substitutes for the unavailable fresh Windows machine for clean installation and non-model
  release smoke
- Docker/WSL2 validates dependency and build reproducibility, not native Windows behavior
- absence of an independent physical tester remains a residual risk
- all heavy model runs continue to require explicit warning and approval

## Scope Decision

The next implementation sprint improves the existing product. It does not add masking, batch editing, mobile,
hosted GPU, new engine families, or a broad model zoo.

## Definition Of Success

The strategy is working when a clean isolated environment can build the project, primary browser workflows have
automated coverage, transient stream loss does not create false job failures, interrupted work has an explicit
attempt/retry record, cancellation is trustworthy, and CPU cost is measured instead of guessed.
