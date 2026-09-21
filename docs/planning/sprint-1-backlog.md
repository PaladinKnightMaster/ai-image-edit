# Sprint 1 Backlog

Status: Historical; Sprint 1 completed
Sprint name: Sprint 1 - Stabilization and Dev Loop
Duration: 2 weeks
Last updated: 2026-04-17
Parent plan: `docs/planning/mvp-war-room-plan.md`
Sprint owner: Tech Lead

## 1. Sprint Goal

Make the project runnable, testable, and fast enough to iterate on from a CPU-only development machine.

This sprint is not for feature expansion. It is for reducing instability and shortening feedback loops so the team can safely build the edit-first MVP in later sprints.

## 2. Definition of Done for Sprint 1

Sprint 1 is complete only when all of the following are true:

- Backend imports and starts cleanly on the development machine
- Frontend builds cleanly
- Fast-check environment can run end to end
- One-engine local smoke flow is reliable
- Main UI no longer exposes obvious non-MVP clutter on the primary workflow
- Minimum smoke validation exists for backend startup and model availability

## 3. Scope Summary

### In Scope

- Fix critical backend startup issue
- Establish fast CPU-only development loop
- Add minimum release and smoke gates
- Reduce obvious main-screen clutter that blocks product focus
- Improve documentation for how to run the project in fast-check mode

### Out of Scope

- Major model integration work
- Full editor UX redesign
- Reference-guided editing feature work
- Android or hosted GPU planning implementation
- OpenVINO hardening

## 4. Epic Breakdown

### Epic A: Runtime Stability

Objective: remove immediate blockers to local execution.

### Epic B: CPU-Only Developer Productivity

Objective: make the project practical to iterate on without waiting hours for every validation cycle.

### Epic C: Minimum Quality Gates

Objective: add cheap checks that catch obvious breakage before the app is used manually.

### Epic D: Product Surface Cleanup

Objective: remove distracting non-MVP UI elements from the primary experience.

### Epic E: Documentation and Runbook

Objective: make the intended Sprint 1 dev loop explicit and repeatable.

## 5. Prioritized Ticket List

Priority scale:

- P0 = must complete in Sprint 1
- P1 = should complete in Sprint 1
- P2 = stretch if capacity remains

---

## Epic A: Runtime Stability

### WR-001 - Fix backend config import blocker

- Priority: P0
- Owner: Backend
- Dependencies: none
- Problem:
  - `backend/app/config.py` has an indentation error that blocks backend startup.
- Tasks:
  - fix the malformed `else` block
  - verify backend import with local venv
  - verify server startup path with current env profile
- Acceptance criteria:
  - `import app.config` succeeds
  - FastAPI app starts without syntax/import failure
  - no regression introduced in config loading behavior

### WR-002 - Verify and normalize model registration behavior

- Priority: P0
- Owner: Backend
- Dependencies: WR-001
- Problem:
  - model docs, manager registration, and model bootstrap are not aligned
- Tasks:
  - review `backend/inference/manager.py`
  - review `backend/app/model_registry.py`
  - review `scripts/mirror_models.py`
  - make sure only supported and documented model paths are presented clearly
- Acceptance criteria:
  - `/api/models` reflects supported runners consistently
  - bootstrap docs do not promise unsupported model flows
  - no ambiguous model state remains for active Sprint 1 engines

### WR-003 - Confirm fast-check environment works end to end

- Priority: P0
- Owner: Backend
- Dependencies: WR-001
- Problem:
  - fast-check profile exists but has not yet been validated as the standard dev loop
- Tasks:
  - run backend with `backend/.env.fast-check`
  - verify DB isolation
  - verify one active model at a time behavior
  - verify startup in local mode
- Acceptance criteria:
  - backend starts with `DOTENV_PATH=backend/.env.fast-check`
  - app uses `app.fast-check.db`
  - local fast-check run path is documented and repeatable

---

## Epic B: CPU-Only Developer Productivity

### WR-004 - Add launcher commands for main and fast-check modes

- Priority: P0
- Owner: DevOps / Backend
- Dependencies: WR-003
- Problem:
  - there is no obvious one-command entry point for switching between normal and fast-check development modes
- Tasks:
  - add backend launch command/script for main mode
  - add backend launch command/script for fast-check mode
  - document frontend startup expectations
- Acceptance criteria:
  - a developer can clearly choose normal vs fast-check mode
  - the selected env profile is explicit
  - instructions work on the target Windows development setup

### WR-005 - Define and document smoke/draft/acceptance preset ladder

- Priority: P0
- Owner: AI/ML
- Dependencies: WR-003
- Problem:
  - the team needs fixed settings for CPU-only iteration instead of ad hoc parameter changes
- Tasks:
  - define per-tier step and resolution ranges
  - define which tier is used for which purpose
  - align env defaults and future UI language
- Acceptance criteria:
  - one documented preset ladder exists
  - devs know when to use smoke, draft, or acceptance
  - draft settings are consistent with fast-check env

### WR-006 - Create benchmark fixture pack v0

- Priority: P1
- Owner: AI/ML
- Dependencies: WR-005
- Problem:
  - there is no fixed reference set for comparing regressions or tuning presets
- Tasks:
  - define initial canonical prompts
  - select initial portrait test images
  - document seeds and evaluation notes
- Acceptance criteria:
  - small benchmark pack exists
  - seeds are fixed
  - benchmark pack is referenced by Sprint 2 work

---

## Epic C: Minimum Quality Gates

### WR-007 - Add backend startup smoke check

- Priority: P0
- Owner: Backend
- Dependencies: WR-001
- Problem:
  - startup/import regressions are too easy to introduce
- Tasks:
  - add a cheap test or check for app import
  - add cheap check for `/health`
  - add cheap check for `/api/models`
- Acceptance criteria:
  - a minimal backend smoke command exists
  - obvious startup regressions are caught without manual clicking

### WR-008 - Add frontend build/lint/type discipline

- Priority: P0
- Owner: Frontend
- Dependencies: none
- Problem:
  - frontend currently has only a thin release discipline
- Tasks:
  - ensure frontend lint remains clean
  - add an explicit typecheck command if missing
  - confirm build passes
- Acceptance criteria:
  - frontend has a minimal validation path
  - build and static checks are part of the normal dev loop

### WR-009 - Define one-engine smoke validation path

- Priority: P1
- Owner: Backend + AI/ML
- Dependencies: WR-003, WR-005
- Problem:
  - the system currently depends too much on heavy full-model manual checks
- Tasks:
  - pick one engine as Sprint 1 smoke engine
  - document minimal run parameters
  - make sure the smoke lane is affordable on CPU
- Acceptance criteria:
  - one standard smoke engine exists
  - one standard smoke run recipe exists
  - Sprint 1 team uses that same recipe consistently

---

## Epic D: Product Surface Cleanup

### WR-010 - Hide non-MVP debug controls from the main workflow

- Priority: P1
- Owner: Frontend
- Dependencies: none
- Problem:
  - failed runs, cleanup, and import/export clutter the main screen
- Tasks:
  - move or hide failed-run management
  - move or hide cleanup controls
  - move or hide import/export thread controls
- Acceptance criteria:
  - the main screen is visually simpler
  - the primary workflow is easier to scan
  - non-essential controls remain accessible only if needed

### WR-011 - Remove arena-first language from the visible shell

- Priority: P1
- Owner: Frontend + Product
- Dependencies: none
- Problem:
  - the current product framing does not match the planned MVP
- Tasks:
  - replace `AI Image Arena` wording
  - remove or de-emphasize arena route from primary UX
  - align shell copy to local studio/editor direction
- Acceptance criteria:
  - first impression is no longer "arena"
  - shell language aligns with MVP direction

---

## Epic E: Documentation and Runbook

### WR-012 - Document fast-check runbook

- Priority: P0
- Owner: DevOps / Tech Lead
- Dependencies: WR-003, WR-004
- Problem:
  - fast-check exists but needs a single authoritative runbook
- Tasks:
  - document backend startup with `DOTENV_PATH`
  - document frontend startup expectations
  - document intended use of fast-check vs main mode
- Acceptance criteria:
  - one concise runbook exists
  - new contributors can follow it without tribal knowledge

### WR-013 - Link planning documents from a discoverable location

- Priority: P2
- Owner: Tech Lead
- Dependencies: none
- Problem:
  - planning docs can be ignored if they are not linked from a visible place
- Tasks:
  - add links from README or docs index if appropriate
  - keep planning docs discoverable but separate from quickstart
- Acceptance criteria:
  - planning docs are easy to find
  - README remains concise

## 6. Recommended Execution Order

1. WR-001 Fix backend config import blocker
2. WR-003 Confirm fast-check environment
3. WR-004 Add launcher commands
4. WR-007 Add backend smoke check
5. WR-008 Add frontend validation path
6. WR-002 Normalize model registration behavior
7. WR-005 Define smoke/draft/acceptance ladder
8. WR-010 Hide non-MVP debug controls
9. WR-011 Remove arena-first language
10. WR-012 Document fast-check runbook
11. WR-006 Create benchmark fixture pack v0
12. WR-009 Define one-engine smoke validation path
13. WR-013 Link planning documents

## 7. Dependencies and Coordination Notes

- Backend and DevOps should coordinate on WR-003 and WR-004.
- Frontend should not begin broad refactoring in Sprint 1; only reduce product-surface clutter and align shell language.
- AI/ML should avoid deep preset work until the smoke/draft/acceptance ladder is defined.
- Product and Tech Lead should review any proposed Sprint 1 work that expands scope beyond stabilization.

## 8. Risks to Sprint 1

### Risk 1: Sprint drifts into feature work

Mitigation:

- reject non-stabilization feature additions
- keep Sprint 1 focused on reliability and feedback loops

### Risk 2: Qwen remains too slow even for draft use

Mitigation:

- keep fast-check defaults aggressive
- choose one smoke engine only
- push full Qwen runs to milestone checkpoints

### Risk 3: UI cleanup grows into a full redesign

Mitigation:

- only remove clutter and correct product language
- defer structural UI redesign to Sprint 2

## 9. Sprint Review Checklist

At sprint close, review:

- Did backend startup become reliable?
- Did the team actually use fast-check mode?
- Did validation time improve?
- Is the main screen less confusing?
- Are planning docs and runbooks enough for the next sprint?
- Is Sprint 2 unblocked?

## 10. Sprint 1 Deliverables

- stable backend startup
- validated fast-check environment
- launcher/run commands for normal and fast-check modes
- minimum backend/frontend validation path
- simplified main UI surface
- documented smoke/draft/acceptance policy
- benchmark fixture pack plan or initial version

## 11. Hand-off to Sprint 2

Sprint 2 should start only after Sprint 1 closes with:

- no known startup blocker
- a working CPU-only fast dev loop
- a simpler main product shell
- clear validation tiers
- no ambiguity around which work is MVP-critical vs deferred
