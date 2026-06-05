# Clean-Machine Release Smoke

Status: Prepared; local workspace smoke passed
Last updated: 2026-06-04
Sprint: Sprint 4
Ticket: WR4-004

## Purpose

This runbook defines the non-model release smoke path for the locked draft-lane beta scope. It verifies
that the repo can start and build on a target machine before any tester invite or off-box acceptance run.

This is not a model-quality benchmark and does not run Qwen edit acceptance.

## Scope

The required release smoke checks are:

- backend fast-check startup smoke
- `/health`, `/ready`, and `/api/models` through the backend smoke test
- frontend lint
- frontend typecheck
- frontend production build
- launch-command sanity for backend and frontend

Inference smoke is optional and approval-gated separately because it can load a model.

## Preconditions

On the target machine:

- repository is cloned
- dependencies are installed or restored
- `backend/.env.fast-check` exists
- `frontend/package.json` dependencies are installed
- model assets required by the selected smoke profile exist if inference smoke will be run

If the repo venv launcher points at a missing base Python, set explicit runtime overrides before smoke:

```powershell
$env:AI_IMAGE_EDIT_PYTHON = "C:\Path\To\python.exe"
$env:AI_IMAGE_EDIT_PYTHON_SITE_PACKAGES = "D:\1_PROJECT\PRIVATE_WORK\ai-image-edit\backend\.venv\Lib\site-packages;D:\1_PROJECT\PRIVATE_WORK\ai-image-edit\.venv\Lib\site-packages"
```

## Required Command

From repo root:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\scripts\release_smoke.ps1
```

This runs:

- `.\scripts\smoke_backend.ps1`
- `npm.cmd run lint`
- `npm.cmd run typecheck`
- `npm.cmd run build`

## Split Commands

Use these when isolating failures.

Backend only:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\scripts\release_smoke.ps1 -SkipFrontend
```

Frontend only:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\scripts\release_smoke.ps1 -SkipBackend
```

Backend launch sanity:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\scripts\start_backend.ps1 -Mode fast-check -NoReload
```

Frontend launch sanity:

```powershell
cd frontend
npm.cmd run dev
```

Use `http://localhost:3000/chat` for browser validation because backend CORS is configured for
`http://localhost:3000`.

## Optional Inference Smoke

Run only when the machine is allowed to load the fast-check smoke model:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\scripts\smoke_qwen_t2i.ps1
```

This requires the backend to already be running in fast-check mode. It is a correctness smoke, not a
quality signoff.

## Pass Criteria

Release smoke passes when:

- backend startup smoke exits 0
- `/health`, `/ready`, and `/api/models` return 200 in the backend smoke test
- frontend lint exits 0
- frontend typecheck exits 0
- frontend build exits 0

## Failure Handling

| Failure | First owner | First action |
| --- | --- | --- |
| Python runtime cannot be resolved | DevOps | Install Python or set `AI_IMAGE_EDIT_PYTHON` plus `AI_IMAGE_EDIT_PYTHON_SITE_PACKAGES`. |
| Backend smoke fails | Backend | Inspect `backend/.env.fast-check`, model allow-list, and DB path. |
| Frontend lint/typecheck fails | Frontend | Fix static issue before beta handoff. |
| Frontend build fails | Frontend + DevOps | Inspect Next build output and env expectations. |
| Optional inference smoke fails | Backend + AI/ML | Treat as smoke-lane blocker, not Qwen acceptance evidence. |

## Evidence To Record

For Sprint 4 release readiness, record:

- date
- machine or environment label
- commit hash
- backend smoke result
- frontend lint/typecheck/build result
- optional inference smoke result, if run
- blockers and owner assignments

## Current Evidence

| Date | Environment | Commit | Result | Notes |
| --- | --- | --- | --- | --- |
| 2026-06-04 | Current Codex workspace | `837d4ef` | pass with warning | Direct run failed before checks because the local venv launcher could not resolve Python. Rerun passed using `AI_IMAGE_EDIT_PYTHON` and repo site-packages override. Backend fast-check smoke, frontend lint, typecheck, and build exited 0. Next build emitted a Windows ESLint cache `EPERM` warning after successful build output. |

Target clean-machine smoke is still required before a tester handoff.
