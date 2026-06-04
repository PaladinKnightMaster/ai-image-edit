# Beta Readiness Checklist

Last updated: 2026-06-04
Sprint: Sprint 3
Status: Draft-lane beta scope locked; not beta-ready for final Qwen acceptance

## Purpose

This document is the Sprint 3 beta gate for the edit-first MVP. It separates product-flow readiness,
local draft-lane evidence, final model-quality evidence, and known limitations so the beta decision is
based on evidence rather than feature count.

## Current Verdict

Do not start a final Qwen-acceptance beta yet.

The edit-first product loop is credible enough for internal dogfooding or a narrowly scoped draft-lane
closed beta if the limitations are explicit. Sprint 4 locks that beta scope in
`docs/planning/beta-scope-decision.md`. The remaining blocker for the intended edit-model beta is off-box
`qwen-image-edit-2511` acceptance evidence.

## Beta Gate Summary

| Gate | Status | Required before closed beta |
| --- | --- | --- |
| Startup and smoke reliability | Partial pass | Keep Sprint 1 startup and smoke checks green on the target beta machine. |
| Edit-first workflow | Pass for local draft lane | Preserve `Edit Photo` as the primary path and keep Create as a supporting draft lane. |
| Reveal and reuse reliability | Pass for current non-model evidence | Keep pending-review reveal/reuse checks green; do not expose unrevealed outputs in normal reuse. |
| Job recovery semantics | Partial pass | Document restart behavior clearly in product/support notes; queued/running jobs currently fail on restart. |
| Preset quality review | Partial pass | Worksheet exists and includes local FLUX draft evidence; Qwen acceptance remains pending. |
| Qwen edit acceptance signoff | Blocked locally | Complete off-box validation or explicitly mark beta as blocked for the intended Qwen edit lane. |
| Runtime expectations | Pass for draft-lane disclosure | CPU-only latency and model-run approval expectations are documented. |
| Known limitations | Pass for internal draft handoff | Tester limitations handoff exists; final invite copy still depends on beta scope. |
| Tester handoff | Pass for owner review | Draft-lane tester handoff is ready in `docs/testing/draft-lane-beta-tester-handoff.md`. |
| Beta scope lock | Pass | Sprint 4 chose draft-lane beta preparation; final Qwen-acceptance beta remains no-go. |
| Release smoke | Partial pass | Current workspace smoke passed with Python override; target clean-machine smoke record is still required. |

## Closed-Beta Entry Criteria

Closed beta can start only when all of these are true:

- Sprint 1 backend launch and smoke checks pass on the target environment.
- Sprint 2 edit-first flow remains intact: base image, optional reference image, preset or prompt,
  result review, compare, download, and reuse.
- Sprint 3 reveal/reuse/recovery checks remain green without launching a model.
- Preset review has a recorded worksheet that labels each result as local FLUX draft evidence,
  Qwen acceptance evidence, blocked, or pending.
- Qwen edit signoff is completed off-box, or the beta scope explicitly excludes final Qwen acceptance.
- Known limitations are visible to the project team and beta testers before use.
- No new engine family, masking surface, batch editing flow, or hosted GPU path is added as a beta dependency.

## Evidence That Counts

### Product-flow evidence

Counts for beta-flow readiness:

- local browser validation on scratch data
- backend API tests that do not launch a model
- frontend lint, typecheck, and production build
- successful reveal and reuse of an existing pending-review output
- successful download/reuse/compare behavior on existing outputs
- scratch-copy reveal/reuse validation for WR3-007 job `dfc36b9bde8d4ee7b111c5196d8ecb24`

### Draft model evidence

Counts only as local draft-lane evidence:

- `flux2-klein-9b-gguf` output and pending-review behavior
- FLUX draft smoke runs approved by the user
- UI behavior around FLUX results, including reveal, compare, download, and reuse
- the 2026-06-03 WR3-007 `flux-draft-smoke` run that reached `pending_review` after 2387 seconds

### Acceptance model evidence

Counts as intended edit-model acceptance evidence:

- off-box `qwen-image-edit-2511` review on the benchmark pack
- recorded preset outcomes against mapped benchmark cases
- reviewer notes for identity preservation, skin realism, lighting coherence, hair detail, artifact absence,
  and instruction adherence

## Known Limitations

- Local `qwen-image-edit-2511` edit signoff is blocked on this machine by a native Windows access violation
  during CPU-only execution.
- `flux2-klein-9b-gguf` is valid for local draft product-flow evidence, not final Qwen acceptance evidence.
- CPU-only edit inference can take tens of minutes and must be presented as long-running background work,
  not a fixed-duration action.
- Queued and running jobs are marked failed on backend restart; there is no durable replay queue yet.
- `pending_review` is a terminal successful generation state for manual-review lanes, but the output must be
  revealed before normal reuse.
- Reference images are optional guidance only; the base image remains the identity/source image.
- The frontend orchestration file remains large; new Sprint 3 work should avoid growing `page.tsx` unless
  extraction is part of the change.
- The current preset benchmark pack uses some proxy fixtures for local draft review and must not be treated
  as acceptance-quality private fixture evidence.

## Beta Decision Options

At Sprint 3 closeout, choose one:

| Option | Use when |
| --- | --- |
| Proceed to closed beta | All gates pass or remaining limitations are explicitly accepted in beta scope. |
| Run one more hardening sprint | Reveal/reuse works, but status copy, preset review, or recovery behavior still needs polish. |
| Delay beta and narrow scope | Qwen edit signoff remains blocked and the beta cannot be scoped honestly around draft-lane evidence. |

## Next Required Artifacts

- off-box Qwen edit validation record from `docs/testing/off-box-qwen-acceptance-packet.md`, or an explicit
  decision that closed beta remains draft-lane only
- clean-machine release smoke record using `docs/testing/clean-machine-release-smoke.md`
- owner-reviewed tester invite/session copy based on `docs/testing/draft-lane-beta-tester-handoff.md`
