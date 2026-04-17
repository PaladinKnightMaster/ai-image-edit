# Session Handoff

## Where the project is
The repo now has:
- MVP roadmap docs
- Sprint 1, 2, and 3 planning docs
- a project-local quality-first war-room operating layer
- fast-check env profiles for CPU-only local iteration
- a durable documentation knowledge base under `docs/index.md`

## What a new session should recover immediately
- product direction: edit-first public MVP
- engineering sequence: stabilize current T2I path first
- dev constraint: CPU-only machine, slow full-model runs
- continuity model: repo-backed docs, not chat-memory
- documentation map: start at `docs/index.md`

## Immediate next action
Start Sprint 1 execution with:
1. fix `backend/app/config.py` indentation at the `FLUX2_ALLOW_SAFETENSORS_LLM` `else:` branch so the backend imports again
2. validate `backend/.env.fast-check`
3. add launcher commands for normal vs fast-check modes
4. keep the new documentation set in sync with implementation changes

## Exact first execution target
- file: `backend/app/config.py`
- problem: backend startup is blocked by an indentation error around the `else:` branch for `FLUX2_ALLOW_SAFETENSORS_LLM`
- success condition: backend imports cleanly and `/health` can start again

## Open caution
Do not broaden scope into new engines or major feature work before Sprint 1 stabilization is complete.
