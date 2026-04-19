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
Continue Sprint 1 with:
1. define benchmark fixture pack v0
2. keep the new documentation set in sync with implementation changes
3. prepare the remaining Sprint 1 work for a clean commit boundary

## Completed in this session
- fixed `backend/app/config.py` indentation for `FLUX2_ALLOW_SAFETENSORS_LLM`
- verified `import app.config` succeeds
- verified `app.main` loads and exposes `/health`
- verified `DOTENV_PATH=backend/.env.fast-check` resolves to `app.fast-check.db`
- verified `/health` and `/api/models` return `200` in fast-check mode
- added `scripts/start_backend.ps1` for explicit `main` vs `fast-check` startup
- added `scripts/smoke_backend.ps1` and `backend/tests/test_startup_smoke.py`
- verified `.\scripts\smoke_backend.ps1 -Mode fast-check` passes
- added frontend `typecheck` and `validate` scripts
- fixed frontend lint warnings in `frontend/app/arena/page.tsx` and `frontend/app/chat/page.tsx`
- verified `npm run lint`, `npm run typecheck`, and `npm run build` all pass
- aligned README/Makefile notes around the canonical Windows backend launch path
- simplified the smoke command to `.\scripts\smoke_backend.ps1`
- reduced the most visible arena-first shell wording in the frontend metadata and headers
- normalized model registration behavior across `backend/inference/manager.py`, `/api/models`, and
  job submission errors
- made invalid `ENABLED_MODELS` values fail fast during startup
- fixed FLUX availability reporting so it matches the active backend path
- surfaced model status detail in the frontend model list and composer state
- documented the smoke/draft/acceptance ladder and aligned fast-check defaults and frontend preset
  language to that vocabulary
- moved failed-run management, cleanup, and thread maintenance behind a collapsed utilities surface in
  the main chat sidebar
- standardized the Sprint 1 smoke inference lane on `qwen-image-2512` and added
  `.\scripts\smoke_qwen_t2i.ps1` as the repeatable smoke command
- reduced the remaining arena-first shell wording so `/arena` is framed as diagnostics and `/chat`
  remains the primary workflow surface

## Open caution
Do not broaden scope into new engines or major feature work before Sprint 1 stabilization is complete.
