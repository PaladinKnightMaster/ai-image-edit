# Current State

Last updated: 2026-06-04

## Product Status
- MVP roadmap drafted
- Sprint 1 through Sprint 4 planning docs drafted
- Sprint 2 editor-first frontend work is engineering-complete for the local draft-lane product scope
- local `qwen-image-edit-2511` benchmark/signoff is blocked on this machine by a reproducible native crash
- the existing `flux2-klein-9b-gguf` lane is available as the local draft edit runtime and completed a
  one-image smoke edit on this machine in about 34.7 minutes, reaching `pending_review` with a usable
  pending output image
- pending-review outputs are now surfaced in Recent runs with an explicit reveal action before reuse
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

## Current Primary Sprint 4 Focus
- Sprint 3 is closed in `docs/planning/sprint-3-closeout-audit.md`
- Sprint 4 is active in `docs/planning/sprint-4-outline.md`
- WR4-001 beta scope is locked in `docs/planning/beta-scope-decision.md`: proceed with draft-lane beta
  preparation only; final Qwen-acceptance beta remains no-go until off-box validation exists
- WR4-002 off-box Qwen acceptance packet is prepared in `docs/testing/off-box-qwen-acceptance-packet.md`;
  execution remains off-box and approval-gated
- WR4-004 clean-machine release smoke is prepared in `docs/testing/clean-machine-release-smoke.md` with
  aggregate script `scripts/release_smoke.ps1`
- current workspace WR4-004 release smoke reran at commit `837d4ef` on 2026-06-04 with explicit Python
  runtime override; target clean-machine smoke remains required before tester handoff
- WR4-005 tester handoff is ready for owner review in `docs/testing/draft-lane-beta-tester-handoff.md`
- WR4-006 fixture decision is locked in `docs/planning/wr3-007-fixture-decision.md`: keep the live
  WR3-007 job pending as a benchmark fixture and use scratch DB copies for routine reveal/reuse checks
- WR4-007 release checklist and risk register is reviewable in
  `docs/planning/sprint-4-release-checklist-and-risk-register.md`; draft-lane beta prep remains
  conditional on target clean-machine smoke and owner-reviewed tester copy
- Sprint 3 local-only pending-review reveal validation and cheap job/recovery checks remain the reliability
  baseline for Sprint 4 release readiness work
- WR3-001 / WR3-003 local reliability coverage has started with temp-DB tests for pending-review reveal,
  API reveal responses, pending-output cleanup on delete, and queued/running recovery after restart
- the existing `data/app.benchmark-review.db` pending-review artifact now has copy-based API validation:
  reveal succeeds against a scratch DB copy while the real benchmark DB remains unchanged
- Recent runs and output-library surfaces now expose stable test hooks for live reveal/reuse browser validation
- WR3-002 has started with a small result-iteration hardening pass: revealed Recent runs now expose
  both `Edit this` and `Download` actions
- reveal actions are now guarded against duplicate submissions and show an in-flight `Revealing...` state
  from both timeline and Recent runs entry points
- live browser validation against a scratch copy of `data/app.benchmark-review.db` passed for Recent runs
  reveal, rendered output, `Edit this` reuse, `Download`, and composer output-library reuse
- landing-state output-library reuse is now browser-validated against the same scratch DB path: the
  landing `Open output library` action opens deterministically, no longer sits under the composer panel,
  and can stage a revealed output as the edit base image
- WR3-008 beta readiness documentation has started in `docs/planning/beta-readiness-checklist.md`;
  the current verdict is not beta-ready yet because preset review and off-box Qwen edit signoff remain incomplete
- WR3-006 preset review documentation has started in `docs/testing/preset-quality-review-worksheet.md`;
  all portrait presets now have mapped cases, evidence lanes, current statuses, and watchouts
- beta tester limitations handoff now exists at `docs/testing/beta-tester-limitations-handoff.md`;
  it is internal draft copy and does not change the current not-beta-ready verdict
- WR3-005 reference-guided UX copy polish has started: UI copy now frames the base image as the
  identity/source image and the optional second image as a visual guide for lighting, style, framing, or angle
- WR3-004 status/error communication now has shared frontend copy helpers plus backend/API presentation
  metadata for queued, running, ready-for-review, complete, failed, restart-recovery, and observer-timeout states
- the status/recovery state contract is documented in `docs/testing/job-status-and-recovery-states.md`
- WR3-007 is prepared but not approved: `docs/testing/wr3-007-draft-preset-review-approval-packet.md`
  defines the local FLUX draft target, preview command, approval-only execution command, and evidence boundaries
- WR3-007 FLUX draft run completed after explicit approval on 2026-06-03: job
  `dfc36b9bde8d4ee7b111c5196d8ecb24` reached `pending_review` in 2387 seconds with pending output image
  `6ea3269b9814425fa91ab6bdf149b01a`; this remains draft evidence only
- WR3-007 reveal/reuse behavior was validated on 2026-06-04 against a scratch copy of the benchmark DB:
  reveal promoted the pending output to reusable `succeeded` state and image retrieval returned 200, while
  the real benchmark DB stayed `pending_review`
- keep Qwen edit benchmark/signoff as an off-box validation lane on stronger hardware

## Active Planning Docs
- `docs/planning/mvp-war-room-plan.md`
- `docs/planning/sprint-1-backlog.md`
- `docs/planning/sprint-2-outline.md`
- `docs/planning/sprint-3-outline.md`
- `docs/planning/sprint-4-outline.md`
- `docs/planning/beta-scope-decision.md`
- `docs/planning/wr3-007-fixture-decision.md`
- `docs/planning/sprint-4-release-checklist-and-risk-register.md`

## Documentation Entry Point
- `docs/index.md`

## Current Recommended Immediate Work
1. run or schedule clean-machine release smoke on the target beta machine
2. owner-review the draft-lane tester handoff copy before any tester invite
3. keep the real WR3-007 pending output unrevealed unless the fixture decision changes explicitly

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
