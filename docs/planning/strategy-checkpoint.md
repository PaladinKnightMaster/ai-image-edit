# Project Strategy Checkpoint

Status: Locked, with a 2026-09-22 studio amendment
Date: 2026-07-16
Owners: War Room Center / Commander + Tech Lead
Decision ADRs:

- `docs/adr/0005-cpu-first-product-and-validation-strategy.md`
- `docs/adr/0006-durable-job-orchestration.md`
- `docs/adr/0007-defer-temporal.md`

## Final Decision

AI Image Edit remains a local, offline-after-setup, edit-first product developed and operated on CPU-only
hardware. No GPU purchase, hosted GPU service, or local GPU dependency is part of the active roadmap.

The project will improve quality in this order:

1. reproducible clean-environment validation
2. automated product-flow coverage
3. trustworthy job transport and status reconciliation
4. durable attempts, cancellation, bounded retry, and restart recovery
5. CPU performance measurement and UI responsiveness
6. Temporal deferred (ADR 0007)
7. benchmark-driven model evaluation

## Runtime Decision

- local default: SQLite-backed orchestration plus existing runner interfaces
- **local mainline (2026-09 amendment):** `sdxl-openvino` for both t2i and prompt-guided edit on CPU
- local optional slow draft: `flux2-klein-9b-gguf`
- intended frontier edit acceptance: `qwen-image-edit-2511` (and eventually Qwen-Image-2.1 if evidence
  supports replacement), off-box / GPU only
- Qwen-Image-2.1 is a catalogued candidate only — not downloaded, not registered, not a release dependency
- experimental orchestration: Temporal deferred by ADR 0007
- selective pattern: Saga compensation for partial side effects only

## Backend + UI Improvement Status (2026-09-22)

Sprint 5 reliability work is closed or deferred. The active roadmap is the private studio, not another runtime.

| Strategy step | Status |
| --- | --- |
| 1. Clean-environment validation | Accepted residual — Sandbox host blocker; not a Sprint 5 gate |
| 2. Automated product-flow coverage | Done for primary mocked flows (WR5-003) |
| 3. Job transport / SSE reconciliation | Done (WR5-004 / PR #6) |
| 4. Durable attempts / cancel / retry / restart | Done (WR5-005–007, PRs #8, #9, #11) |
| 5. CPU + UI performance baseline | Done (WR5-008); report in `docs/planning/cpu-ui-performance-baseline.md` |
| 6. Optional Temporal spike | Deferred — ADR 0007; no Temporal install |
| 7. Benchmark-driven model evaluation | Candidate noted only (WR5-010 / Qwen-Image-2.1); off-box only |
| 8. Private studio surface | Active — PR #16 folder confirmation, PR #17 rail + gallery. Next: real preset thumbnails |

## Studio Amendment (2026-09-22)

The daily screen follows online create pages and prompt galleries, adapted for one local user.

- pin the prompt and Run edit
- show portrait presets as a visual library
- show recent runs as the private gallery
- keep Hardware fit, model folder, runtime stats, and the model list inside a collapsible rail
- do not add a public Explore feed, a top mode menu, or a second models column

## Validation Decision

- Windows Sandbox remains the preferred clean-Windows surrogate when the host feature works.
  On this machine the host crash is an accepted residual and is not a Sprint 5 gate.
- Docker/WSL2 validates dependency and build reproducibility, not native Windows behavior
- absence of an independent physical tester remains a residual risk
- all heavy model runs continue to require explicit warning and approval

## Scope Decision

The next implementation work improves the studio on the existing CPU runtime. It does not add masking, batch
editing, a mobile app, hosted GPU, new engine families, or a broad model zoo.

## Definition Of Success

The strategy is working when a clean isolated environment can build the project, primary browser workflows have
automated coverage, transient stream loss does not create false job failures, interrupted work has an explicit
attempt/retry record, cancellation is trustworthy, and CPU cost is measured instead of guessed.
