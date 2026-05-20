# Beta Readiness Checklist

Last updated: 2026-05-20
Sprint: Sprint 3
Status: Not beta-ready yet

## Purpose

This document is the Sprint 3 beta gate for the edit-first MVP. It separates product-flow readiness,
local draft-lane evidence, final model-quality evidence, and known limitations so the beta decision is
based on evidence rather than feature count.

## Current Verdict

Do not start closed beta yet.

The edit-first product loop is credible enough for continued hardening, and the manual-review reveal
path now has non-model API and browser evidence. The remaining blockers are preset quality review,
off-box Qwen edit signoff, and explicit beta limitations copy.

## Beta Gate Summary

| Gate | Status | Required before closed beta |
| --- | --- | --- |
| Startup and smoke reliability | Partial pass | Keep Sprint 1 startup and smoke checks green on the target beta machine. |
| Edit-first workflow | Pass for local draft lane | Preserve `Edit Photo` as the primary path and keep Create as a supporting draft lane. |
| Reveal and reuse reliability | Pass for current non-model evidence | Keep pending-review reveal/reuse checks green; do not expose unrevealed outputs in normal reuse. |
| Job recovery semantics | Partial pass | Document restart behavior clearly in product/support notes; queued/running jobs currently fail on restart. |
| Preset quality review | Not complete | Record a preset review worksheet with lane labels and outcome notes before beta. |
| Qwen edit acceptance signoff | Blocked locally | Complete off-box validation or explicitly mark beta as blocked for the intended Qwen edit lane. |
| Runtime expectations | Partial pass | Document CPU-only latency and model-run approval expectations for testers. |
| Known limitations | Partial pass | Publish a concise limitations note before beta invite or tester handoff. |

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

### Draft model evidence

Counts only as local draft-lane evidence:

- `flux2-klein-9b-gguf` output and pending-review behavior
- FLUX draft smoke runs approved by the user
- UI behavior around FLUX results, including reveal, compare, download, and reuse

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

- WR3-006 preset quality review worksheet
- concise beta known-limitations handoff for testers: `docs/testing/beta-tester-limitations-handoff.md`
- off-box Qwen edit validation record, or an explicit decision that closed beta is draft-lane only
