# Current State

Last updated: 2026-04-17

## Product Status
- MVP roadmap drafted
- Sprint 1, Sprint 2, and Sprint 3 planning docs drafted
- fast-check env profiles added for CPU-only development
- war-room operating layer added as project-local architecture

## Known Critical Blocker
- backend startup is currently blocked by a syntax error in `backend/app/config.py`

## Active Planning Docs
- `docs/planning/mvp-war-room-plan.md`
- `docs/planning/sprint-1-backlog.md`
- `docs/planning/sprint-2-outline.md`
- `docs/planning/sprint-3-outline.md`

## Current Recommended Immediate Work
1. fix backend startup blocker
2. validate fast-check environment
3. add launch scripts for main vs fast-check modes
4. reduce non-MVP UI clutter

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
