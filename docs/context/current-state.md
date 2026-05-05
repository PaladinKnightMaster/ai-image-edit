# Current State

Last updated: 2026-04-28

## Product Status
- MVP roadmap drafted
- Sprint 1, Sprint 2, and Sprint 3 planning docs drafted
- Sprint 2 editor-first frontend work is largely implemented
- local `qwen-image-edit-2511` benchmark/signoff is blocked on this machine by a reproducible native crash
- the existing `flux2-klein-9b-gguf` lane is available as the local draft edit runtime
- fast-check env profiles added for CPU-only development
- war-room operating layer added as project-local architecture
- durable ADR, architecture, workflow, model, design, and testing docs added under `docs/`

## Resolved Sprint 1 Work
- backend startup blocker in `backend/app/config.py` is fixed
- fast-check backend profile has been validated against `/health` and `/api/models`
- Windows-friendly backend launcher command now exists for `main` vs `fast-check`
- backend fast-check smoke command now exists and passes
- frontend validation path now exists with `npm run lint`, `npm run typecheck`, and `npm run build`
- launch-path docs and smoke command interface have been aligned
- highest-visibility arena-first shell copy has been reduced
- model registration/runtime status is now normalized across `/api/models`, job submission, and docs
- invalid `ENABLED_MODELS` values now fail fast instead of silently hiding all runners
- FLUX status now reflects the active backend path instead of optimistic asset detection
- smoke/draft/acceptance ladder is now documented and aligned with fast-check defaults and UI labels
- maintenance, cleanup, failed-run recovery, and thread import/export controls are now collapsed behind
  a secondary utilities surface in the main chat workflow
- Sprint 1 now has a standard smoke inference engine and run recipe: `qwen-image-2512`
- remaining arena-first shell language has been reduced to diagnostics-first wording on secondary
  surfaces and docs
- benchmark fixture pack v0 now exists with fixed seeds, case ids, and local asset slot conventions
  for Sprint 2 and Sprint 3 validation work
- backend launcher and startup smoke scripts now validate Python runtime viability and can fall back
  to the base interpreter plus venv site-packages when the Windows venv launcher is stale

## Current Primary Sprint 2 Focus
- finish the remaining Sprint 2 product work without waiting on local `qwen-image-edit-2511` recovery
- use the now capability-aware `flux2-klein-9b-gguf` lane as the local draft edit path on this machine
- validate the FLUX draft lane with one explicitly approved one-image smoke edit before leaning on it day to day
- keep Qwen edit benchmark/signoff as an off-box validation lane on stronger hardware

## Active Planning Docs
- `docs/planning/mvp-war-room-plan.md`
- `docs/planning/sprint-1-backlog.md`
- `docs/planning/sprint-2-outline.md`
- `docs/planning/sprint-3-outline.md`

## Documentation Entry Point
- `docs/index.md`

## Current Recommended Immediate Work
1. run one explicitly approved FLUX one-image draft edit smoke on this machine
2. use the FLUX local draft lane for continued Sprint 2 product verification and polish
3. keep `qwen-image-edit-2511` benchmark/signoff deferred to a stronger machine instead of forcing local reruns

## Supported Runtime Lanes
- `qwen-image-2512` - local T2I smoke lane
- `qwen-image-edit-2511` - intended edit benchmark/signoff lane, blocked locally on this machine
- `flux2-klein-9b-gguf` - local draft T2I + edit lane via the existing repo fallback path
- `sdxl-openvino` exists but is not MVP-core yet

## Operating Model
- use one commander voice
- use the minimum useful specialist set
- expand depth when quality or confidence requires it
- use repo docs as continuity, not prior chat memory
