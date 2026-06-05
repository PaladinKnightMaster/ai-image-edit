# Session Handoff

## Where the project is
The repo now has:
- MVP roadmap docs
- Sprint 1 through Sprint 4 planning docs
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
Continue Sprint 4 from the locked beta scope:
1. start from `docs/planning/sprint-3-closeout-audit.md`
2. review `docs/planning/sprint-4-outline.md`
3. use `docs/planning/beta-scope-decision.md` as the WR4-001 decision record
4. WR4-002 is prepared in `docs/testing/off-box-qwen-acceptance-packet.md`
5. WR4-004 is prepared in `docs/testing/clean-machine-release-smoke.md`
6. WR4-005 is owner-reviewed in `docs/testing/draft-lane-beta-tester-handoff.md`; tester invite remains
   gated by target clean-machine smoke
7. WR4-006 is locked in `docs/planning/wr3-007-fixture-decision.md`: keep the real WR3-007 pending
   output as a fixture and validate reveal/reuse against scratch DB copies
8. WR4-007 is reviewable in `docs/planning/sprint-4-release-checklist-and-risk-register.md`
9. next run or schedule target clean-machine release smoke, then record the result or owner-assigned blocker
10. do not submit a new edit job or run any model unless the user explicitly approves a heavy run

## Completed in this session
- started WR3-004 status/error communication with `frontend/app/chat/status-copy.ts`
- replaced raw frontend status labels such as `pending_review` with user-facing labels such as
  `Ready for review`, and added short explanations for queued, running, ready-for-review, complete, failed,
  restart-recovery, and observer-timeout states across timeline, Recent runs, and failed-run recovery
- added backend/API status presentation metadata on job and run responses: `status_label`, `status_detail`,
  `stage_label`, and `error_detail`
- documented the status/recovery state contract in `docs/testing/job-status-and-recovery-states.md`
- prepared WR3-007 without execution in `docs/testing/wr3-007-draft-preset-review-approval-packet.md`,
  including the preview command, approval-only FLUX draft command, expected cost, evidence fields, and go/no-go criteria
- recorded the 2026-06-03 approved WR3-007 FLUX draft run: job `dfc36b9bde8d4ee7b111c5196d8ecb24`,
  run `37706e19de514559a21a0696d3705d5d`, pending output `6ea3269b9814425fa91ab6bdf149b01a`,
  `pending_review` after 2387 seconds, wrapper exit `0x00000000`
- validated WR3-007 reveal/reuse against a scratch DB copy without launching a model: reveal promoted the
  copied job to `succeeded`, cleared `pending_output_image_id`, exposed the run in reusable history, returned
  image 200, and left the real benchmark DB unchanged at `pending_review`
- closed Sprint 3 in `docs/planning/sprint-3-closeout-audit.md`
- proposed Sprint 4 in `docs/planning/sprint-4-outline.md` as a beta scope lock and acceptance validation sprint
- locked WR4-001 beta scope in `docs/planning/beta-scope-decision.md`: draft-lane beta preparation is allowed
  with explicit limitations, final Qwen-acceptance beta remains no-go until off-box validation exists
- prepared WR4-002 in `docs/testing/off-box-qwen-acceptance-packet.md` and expanded
  `scripts/run_edit_benchmark_case.ps1` so off-box runs can pass explicit dotenv, model-root, and DB paths
- prepared WR4-004 with `docs/testing/clean-machine-release-smoke.md` and `scripts/release_smoke.ps1`
- finalized WR4-005 tester handoff for owner review in `docs/testing/draft-lane-beta-tester-handoff.md`
- locked WR4-006 in `docs/planning/wr3-007-fixture-decision.md`: live WR3-007 remains pending as a
  benchmark fixture, while routine reveal/reuse regression checks should use scratch DB copies
- prepared WR4-007 in `docs/planning/sprint-4-release-checklist-and-risk-register.md`, including release
  gates, known blockers, evidence commands, owner actions, and the Sprint 4 exit readiness checklist
- reran non-model release smoke at commit `837d4ef`: direct run failed on local Python launcher resolution,
  rerun with `AI_IMAGE_EDIT_PYTHON` plus repo site-packages override passed backend fast-check smoke,
  frontend lint, typecheck, and build; target clean-machine smoke is still required
- owner-reviewed the draft-lane beta tester handoff and limitations copy; it now blocks tester invite on
  target clean-machine smoke and explicitly says local FLUX draft outputs are not final Qwen quality evidence
- added `AI_IMAGE_EDIT_PYTHON` / `AI_IMAGE_EDIT_PYTHON_SITE_PACKAGES` runtime overrides after release smoke
  exposed stale venv launcher metadata on this machine
- started WR3-005 reference-guided UX copy polish without adding controls:
  `ModeSwitchHero`, `WorkflowLandingState`, `ComposerPanel`, `HistoryPickerModal`, `BeforeAfterCompare`,
  and related notices now distinguish base identity/source image from optional visual guide image
- updated `docs/workflows/user-workflows.md` so reference-guided edit explicitly says the reference is
  visual guidance for lighting, style, framing, or angle, not a replacement subject or identity
- added `docs/testing/beta-tester-limitations-handoff.md` as an internal draft for future closed-beta
  tester messaging, including current scope, what testers can evaluate, what is not final, known limitations,
  feedback prompts, and the current go/no-go message
- linked the beta tester limitations handoff from `docs/index.md`, `docs/planning/beta-readiness-checklist.md`,
  and the Sprint 3/current-state docs
- added `docs/testing/preset-quality-review-worksheet.md` for WR3-006 with every Sprint 2 portrait preset
  mapped to benchmark cases, evidence lanes, current statuses, review dimensions, watchouts, and review-log fields
- linked the preset quality worksheet from `docs/index.md` and `docs/testing/preset-benchmark-review.md`
- added `docs/planning/beta-readiness-checklist.md` for WR3-008 with the current not-beta-ready verdict,
  closed-beta gates, evidence tiers, known limitations, and Sprint 3 beta decision options
- linked the beta readiness checklist from `docs/index.md` and updated Sprint 3/current-state docs so the
  next non-model step is WR3-006 preset review worksheet plus beta tester limitations handoff
- hardened the landing-state output-library entry by adding a stable test hook, an in-flight loading guard,
  and a layout fix that removes the composer panel's desktop sticky overlap from timeline/landing controls
- ran live browser validation with backend/frontend on localhost against a scratch DB copy:
  landing `Open output library` opens the history picker, the copied pending-review run can be revealed,
  the revealed output appears in the landing output library, and `Use as base image` stages it for editing
- confirmed the scratch DB reveal moved pending image `340ab221970549709dc9d017b96b3cba` to
  `output_image_id`, cleared `pending_output_image_id`, and set the copied job to `succeeded`; the real
  `data/app.benchmark-review.db` fixture remains `pending_review`
- added copy-based API validation using `data/app.benchmark-review.db` as a read-only source fixture:
  the test copies the DB, reveals job `64ff0fcdc35b42c3b46e35be413c8e48` in the scratch copy, verifies
  `/api/jobs`, `/api/runs?status=...`, and `/api/images`, then confirms the real benchmark DB is unchanged
- added stable `data-testid` hooks to Recent runs reveal/reuse controls and the output-library reuse cards so
  the next browser validation can target deterministic elements
- started WR3-002 result-iteration hardening by adding a direct `Download` action to revealed Recent runs
  alongside `Edit this`
- hardened reveal UI against duplicate submissions with a shared in-flight `Revealing...` state for both
  timeline and Recent runs reveal actions
- ran live browser validation with backend/frontend on localhost against a scratch DB copy:
  Recent runs `Reveal` changed the fixture from `pending_review` to `succeeded`, rendered the output,
  exposed `Edit this` and `Download`, staged the revealed output as the edit base, and confirmed the
  composer output-library replacement path shows the revealed run as reusable
- note: use `http://localhost:3000/chat` for browser validation because backend CORS is configured for
  `http://localhost:3000`; `127.0.0.1:3000` loads the page but client-side API reads are blocked by CORS
- started WR3-001 / WR3-003 as a local-only reliability slice without submitting a new edit job or running a model
- added cheap temp-DB backend coverage for pending-review reveal transitions: pending output moves to
  `output_image_id`, `pending_output_image_id` clears, job status becomes `succeeded`, and run history becomes reusable
- added in-process API coverage for `POST /api/jobs/{job_id}/reveal`, `GET /api/jobs/{job_id}`, and
  `GET /api/runs?status=...` against a seeded pending-review run
- added cheap coverage for pending-review run deletion with pending-output image cleanup
- exposed job restart recovery as `recover_interrupted_jobs()` and covered queued/running jobs becoming failed with
  `server restarted` while succeeded jobs remain intact
- confirmed read-only that `data/app.benchmark-review.db` still has pending-review job
  `64ff0fcdc35b42c3b46e35be413c8e48` with pending image `340ab221970549709dc9d017b96b3cba`
- confirmed the approved `flux2-klein-9b-gguf` one-image smoke edit completed on CPU in about 34.7
  minutes, reached `pending_review`, and produced pending image `340ab221970549709dc9d017b96b3cba`
- completed the Sprint 2 closeout audit in `docs/planning/sprint-2-closeout-audit.md`, marking the
  local draft-lane product scope engineering-complete while preserving Qwen edit signoff as off-box work
- activated Sprint 3 in `docs/planning/sprint-3-outline.md` with reliability, reveal, iteration, preset-review,
  and beta-readiness work sequenced before any approval-gated model-quality run
- surfaced pending-review outputs in Recent runs with an explicit `Reveal` action, while keeping unrevealed
  outputs out of normal edit reuse/history selection
- identified a harness classification bug: `pending_review` was not treated as terminal, so the wrapper
  kept polling until `MaxWaitSec` and reported `observer_timeout` after successful generation
- exposed `pending_output_image_id` in the job/run API response and updated the benchmark harness to stop
  on `pending_review`, capture the pending output path, and return success for `pending_review` smoke runs
- added persisted job activity fields (`stage`, progress step/percent/total, and `last_activity_at`) so
  the UI, polling API, SSE reconnects, and benchmark harness share the same long-running job state
- changed the benchmark harness so `MaxWaitSec` is an observer timeout, not an automatic job failure;
  observer timeouts now exit distinctly without calling `mark_job_failed`
- raised the approval-gated benchmark wrapper default observer window to 7200 seconds and labeled exit
  code `2` as `observer_timeout`
- added timeline copy for active local inference so slow CPU runs are represented as continuing work
  rather than unexplained silence
- added `flux-draft-smoke` to the approval-gated edit review runner so the next model run targets FLUX local draft editing rather than the blocked Qwen edit lane
- passed `strength` through the review harness edit payload for FLUX img2img smoke coverage
- operationalized the local `flux2-klein-9b-gguf` draft edit lane in the product surface instead of leaving it as a hidden special case
- added backend `/api/models` metadata for `edit_input_limit` so edit runners now declare their real input-image constraints
- made the chat flow capability-aware so edit mode now defaults to FLUX locally, reference-image UI is gated by model metadata, and single-image edit lanes automatically normalize attachments to a valid base-only state
- replaced FLUX-only frontend checks for edit-attachment count and strength controls with metadata-driven behavior where possible
- verified the FLUX draft-lane implementation with backend model-registration tests plus `npm.cmd run lint`, `npm.cmd run typecheck`, and `npm.cmd run build`
- approved the war-room pivot away from local `qwen-image-edit-2511` benchmark attempts on this PC and toward the existing `flux2-klein-9b-gguf` lane for local draft edit work
- confirmed the local FLUX lane is present and reported by `/api/models` as a valid `t2i + edit` runtime through the existing repo fallback path
- captured the second `Headshot Cleanup` rerun failure as a native process exit with `wrapper_exit_code = -1073741819` (`0xC0000005`, access violation) after about 104 seconds of CPU-only progress, with the job still left `running` and no output image
- taught `scripts/run_edit_benchmark_case.ps1` to decode common native process exit codes into `wrapper_exit_hex` / `wrapper_exit_meaning` for future crash reports
- hardened the benchmark runner again so the summary records per-poll heartbeats and the PowerShell wrapper stamps `wrapper_exit_code` / `wrapper_finished_at`, marking `process_exit` when Python disappears before a terminal status write
- hardened `scripts/run_edit_benchmark_case.py` so it writes `data/benchmark-review-summary.json` immediately and updates it incrementally during upload, submission, and polling, reducing artifact loss when CPU-only model startup dies mid-run
- hardened the approval-gated benchmark runner against Windows PowerShell UTF-8 BOM temp-plan files after a real user repro
- added `scripts/run_edit_benchmark_case.ps1` as an approval-gated PowerShell entrypoint for preset benchmark review targets
- added `scripts/run_edit_benchmark_case.py` as the long-lived in-process upload/job/poll harness that can keep `qwen-image-edit-2511` loaded across review targets
- added a durable war-room rule that all agents must notify the user and get approval before heavy model execution
- proved the first exact-coverage benchmark path end-to-end through upload and queued edit submission using the staged proxy fixture pack and `qwen-image-edit-2511`
- recorded a measured runtime blocker: `Headshot Cleanup` / `edit-001-headshot-cleanup` reached `running` but produced no output within a bounded CPU-only harness window
- corrected `docs/testing/preset-benchmark-review.md` so the proxy-pack worksheet is explicitly `Draft` tier rather than `Acceptance`
- staged a temporary local proxy fixture pack under `fixtures/private/benchmark-pack-v0/` by copying existing workspace outputs from `data/images/` into the canonical benchmark filenames
- documented the proxy fixture mapping and usage limits in `docs/testing/preset-benchmark-review.md`
- confirmed the `qwen-image-edit-2511` mirrored asset tree exists locally under `models/hf/Qwen/Qwen-Image-Edit-2511`
- worked around the broken system Python path by using the bundled workspace runtime for the first in-process review harness
- attempted to start the first manual preset review and confirmed this workspace does not yet contain the private benchmark fixtures under `fixtures/private/benchmark-pack-v0/`
- extended `docs/testing/preset-benchmark-review.md` with an explicit prerequisite checklist, first-pass preset order, and a lightweight acceptance review worksheet
- extended `frontend/app/chat/edit-presets.ts` with benchmark review metadata so each portrait preset now carries mapped benchmark cases, shared review dimensions, and explicit watchouts
- added `docs/testing/preset-benchmark-review.md` as the lightweight execution note that maps Sprint 2 presets to `benchmark-pack-v0`
- marked the reference-guided benchmark cases as active in `docs/testing/benchmark-pack.md` and `docs/testing/benchmark-pack.v0.json` now that the base/reference workflow is live
- updated `docs/testing/test-strategy.md` and `docs/index.md` so the benchmark-review note is part of the durable testing map
- polished remaining onboarding and helper copy so `/chat` reads more like an edit-first studio and less
  like a generic chat shell
- updated helper surfaces from `thread` / `history` language toward `session` / `output library`
  terminology where it is user-facing
- aligned create-mode labels around `Create draft` / `starter prompts` and changed the result lane label
  from `Assistant` to `Studio engine`
- verified the copy/onboarding polish slice with `npm.cmd run lint`, `npm.cmd run typecheck`, and
  `npm.cmd run build`
- moved model selection and raw tuning behind an explicit `Advanced controls` drawer in
  `frontend/app/chat/components/ComposerPanel.tsx`
- presets, prompt, and `Base image` / `Reference image` slots now remain visually primary while
  model choice, run profile, and numeric controls are secondary
- added drawer summary chips for active model, manual-review state, and missing-files state so the
  user still sees essential runtime context without opening raw controls
- verified the advanced-controls drawer slice with `npm.cmd run lint`, `npm.cmd run typecheck`, and
  `npm.cmd run build`
- made the composer explicitly model one `Base image` plus one optional `Reference image`
- slot-specific upload and history actions now target `base` vs `reference` instead of a generic
  two-image bucket
- edit submission now preserves `base`-first ordering in request snapshots so compare and reuse flows
  can identify the true source image reliably
- history picker now labels actions as `Use as base image` vs `Use as reference image`
- timeline attachment badges now clarify `Base` / `Reference` and source provenance
- verified the explicit base/reference workflow with `npm.cmd run lint`, `npm.cmd run typecheck`,
  and `npm.cmd run build`
- added `frontend/app/chat/components/BeforeAfterCompare.tsx` as a lightweight per-result compare widget
- edit results with recoverable base inputs now support `Before`, `Split`, and `After` comparison inside
  the main timeline
- compare now prefers the explicit `base` image slot and surfaces when extra reference inputs are
  present but outside the compare view
- verified the compare slice with `npm.cmd run lint`, `npm.cmd run typecheck`, and `npm.cmd run build`
- implemented generated-image-to-edit polish so successful outputs now expose explicit `Edit this` actions
- direct output handoff now switches to `Edit Photo`, stages the selected result as the new base image,
  and clears stale create-mode prompt state
- added composer feedback when a generated or history output is staged for editing
- labeled staged attachments and message-history snapshots as `Generated result` vs `History`
- verified the generated-image-to-edit slice with `npm.cmd run lint`, `npm.cmd run typecheck`, and
  `npm.cmd run build`
- extracted `frontend/app/chat/components/HistoryPickerModal.tsx` for the edit-input history overlay
- extracted `frontend/app/chat/components/UtilitiesPanel.tsx` for import/export, cleanup, and failed-run recovery controls
- verified the modal/sidebar extraction with `npm.cmd run lint`, `npm.cmd run typecheck`, and
  `npm.cmd run build`
- added `frontend/app/chat/edit-presets.ts` as the structured portrait preset metadata source
- added preset types to `frontend/app/chat/types.ts` and wired preset application through the page state
- implemented portrait preset picker v1 in `frontend/app/chat/components/ComposerPanel.tsx`
- selecting a portrait preset now populates the edit prompt and applies draft-tier defaults for the
  current edit flow
- verified the preset picker slice with `npm.cmd run lint`, `npm.cmd run typecheck`, and
  `npm.cmd run build`
- extracted `frontend/app/chat/components/MessageTimeline.tsx` for the message stream and empty-state flow
- extracted `frontend/app/chat/components/ComposerPanel.tsx` for model selection, prompt input,
  attachments, and settings
- added `frontend/app/chat/types.ts` as the shared type surface for the new chat components
- verified the timeline/composer extraction with `npm.cmd run lint`, `npm.cmd run typecheck`, and
  `npm.cmd run build`
- extracted the top shell into `frontend/app/chat/components/ModeSwitchHero.tsx`
- added an edit-first landing state in `frontend/app/chat/components/WorkflowLandingState.tsx`
- reworked the empty `/chat` experience so it teaches the edit workflow and keeps create as the
  supporting lane
- verified the extracted-shell slice with `npm.cmd run lint`, `npm.cmd run typecheck`, and
  `npm.cmd run build`
- introduced explicit `Edit Photo` / `Create from Scratch` mode state in `frontend/app/chat/page.tsx`
- removed attachment-count inference as the primary mode switch; model filtering, CTA copy, prompt copy,
  validation, and settings gating now follow explicit mode
- preserved `Use as input` behavior by switching into edit mode when history or generated outputs are reused
- verified the frontend slice with `npm.cmd run lint`, `npm.cmd run typecheck`, and `npm.cmd run build`
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
- created benchmark fixture pack v0 with fixed seeds, stable case ids, and local private asset slot
  conventions for Sprint 2 and Sprint 3 validation work
- hardened backend launcher and startup smoke scripts so they can fall back to the base interpreter
  plus venv site-packages when the Windows venv launcher is stale

## Open caution
Do not broaden scope into new engines or major feature work before Sprint 1 stabilization is complete.
