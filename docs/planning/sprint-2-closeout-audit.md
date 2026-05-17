# Sprint 2 Closeout Audit

Date: 2026-05-17
Mode: War Room closeout audit
Scope: Sprint 2 editor-first UX and core editing flow

## Verdict

Sprint 2 is engineering-complete for the local draft-lane product scope.

The edit-first product flow now exists end to end:

1. choose `Edit Photo`
2. add a base image
3. optionally add a reference image when the active model supports it
4. choose a portrait preset or write an instruction
5. run an edit
6. review the result
7. reveal manual-review outputs when needed
8. compare before/after
9. download or reuse the output for another edit round

The remaining limitation is not a Sprint 2 product-flow blocker. Local `qwen-image-edit-2511`
benchmark/signoff remains blocked by the current CPU-only Windows environment and must be handled as
an off-box validation lane. The local FLUX draft lane is valid for product-flow evidence, not final
Qwen acceptance evidence.

## Definition Of Done Audit

| Requirement | Status | Evidence |
| --- | --- | --- |
| Primary entry experience is explicitly edit-first | Pass | `ModeSwitchHero` labels `Edit Photo` as primary mode and `Create from Scratch` as secondary. `workflowMode` defaults to `edit`. |
| Clean `upload -> edit -> compare -> save` flow | Pass with local validation caveat | `ComposerPanel` models base/reference input slots, edit prompt, presets, and submit action. `MessageTimeline` renders compare and download actions for outputs. Pending-review outputs require reveal first. |
| `Create from Scratch` remains available as secondary mode | Pass | `ModeSwitchHero` and `WorkflowLandingState` keep create mode available but route users back toward edit. |
| Generated images can become edit inputs in one click | Pass | `startEditFromOutput` switches to edit mode and stages the selected output as the base image. |
| Frontend structure is materially more maintainable | Pass with residual debt | Product components now exist for mode switch, landing state, composer, timeline, compare, history picker, and utilities. Residual debt: `page.tsx` is still a large orchestration file and should be split into hooks in Sprint 3 or hardening. |
| Preset-driven editing exists in usable first version | Pass | `edit-presets.ts` contains six portrait presets with prompt templates, draft defaults, benchmark mappings, and watchouts. |

## Ticket Audit

| Ticket | Status | Notes |
| --- | --- | --- |
| WR2-001 - Explicit product mode switch | Done | User-facing `Edit Photo` / `Create from Scratch` mode split is implemented. |
| WR2-002 - Reframe landing around editing | Done | Empty state and mode hero explain editing as the primary workflow. |
| WR2-003 - Split main chat page into components | Done with debt | Major UI surfaces are extracted. `page.tsx` still owns job orchestration, SSE, replay, reveal, and attachment state. |
| WR2-004 - Generated-image-to-edit handoff | Done | Outputs expose `Edit this`; handoff stages generated output as the edit base. |
| WR2-005 - Preset system v1 | Done | Structured preset metadata is implemented and used by the composer. |
| WR2-006 - Optional reference-image workflow | Done | Base/reference slots are explicit and gated by model `edit_input_limit`. |
| WR2-007 - Before/after compare | Done | Compare supports before, split, and after modes without rerunning the job. |
| WR2-008 - Advanced controls drawer | Done | Model and raw tuning controls are secondary behind an explicit drawer. |
| WR2-009 - Preset validation where runtime permits | Constrained complete | FLUX draft smoke produced usable pending-review output. Qwen edit signoff is deferred off-box due local native crash. |
| WR2-010 - Product copy and onboarding hints | Done | Copy now frames the app as an edit-first studio. |
| WR2-011 - Surface manual-review outputs | Done | Recent runs exposes pending-review outputs with `Reveal`; unrevealed outputs are excluded from normal reuse. |

## Residual Risks

- `page.tsx` remains 1,947 lines and still combines state orchestration, job lifecycle, attachment handling,
  replay, reveal, and rendering composition. This is acceptable for Sprint 2 closeout but should not grow
  further.
- The manual-review reveal path has build/type validation but should still get a lightweight live UI or API
  check against an existing `pending_review` run before public-beta hardening.
- FLUX local draft evidence cannot be used as final acceptance evidence for the intended Qwen edit lane.
- The current CPU-only machine makes runtime timing highly variable; UX must continue to treat long inference
  as background work with persisted activity, not as a fixed-duration action.

## Recommended Next Step

Move to Sprint 3 planning/start with two inherited constraints:

1. Keep Qwen edit benchmark/signoff as an explicit off-box validation task.
2. Prioritize result-iteration reliability, preset quality review, and job/reveal hardening before adding new
   editing surfaces such as masking or batch workflows.
