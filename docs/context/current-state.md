# Current State

Last updated: 2026-04-17

## Product Status
- MVP roadmap drafted
- Sprint 1, Sprint 2, and Sprint 3 planning docs drafted
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

## Current Primary Sprint 1 Focus
- reduce non-MVP UI clutter
- define smoke/draft/acceptance ladder
- pick and document one-engine smoke validation path

## Active Planning Docs
- `docs/planning/mvp-war-room-plan.md`
- `docs/planning/sprint-1-backlog.md`
- `docs/planning/sprint-2-outline.md`
- `docs/planning/sprint-3-outline.md`

## Documentation Entry Point
- `docs/index.md`

## Current Recommended Immediate Work
1. reduce non-MVP UI clutter
2. define smoke/draft/acceptance ladder
3. pick and document one-engine smoke validation path
4. keep Sprint 1 docs in sync with implementation

## Supported Runtime Lanes
- `qwen-image-2512`
- `qwen-image-edit-2511`
- `flux2-klein-9b-gguf`
- `sdxl-openvino` exists but is not MVP-core yet

## Operating Model
- use one commander voice
- use the minimum useful specialist set
- expand depth when quality or confidence requires it
- use repo docs as continuity, not prior chat memory
