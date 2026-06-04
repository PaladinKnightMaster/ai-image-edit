# Preset Quality Review Worksheet

Last updated: 2026-06-04
Sprint: Sprint 3
Ticket: WR3-006
Status: FLUX draft evidence recorded; Qwen acceptance remains off-box

## Purpose

This worksheet is the active Sprint 3 record for preset quality review. It keeps preset tuning decisions
separate from live model execution and labels every result by evidence lane.

Use this file to decide what needs review, what evidence already exists, and what cannot be claimed yet.

## Evidence Lanes

| Lane | Meaning | Can count for |
| --- | --- | --- |
| `local-product-flow` | Browser/API/UI evidence using existing outputs or scratch data, without launching a model. | Workflow readiness only. |
| `flux-draft` | Approved `flux2-klein-9b-gguf` draft-lane result. | Local draft behavior and UI flow evidence. |
| `qwen-acceptance` | Off-box `qwen-image-edit-2511` benchmark result on the mapped case. | Intended edit-model quality signoff. |
| `blocked-local` | Local attempt cannot complete because of current machine/runtime constraints. | Blocker evidence only. |

Do not promote `flux-draft` evidence to `qwen-acceptance`.

## Outcome Scale

| Outcome | Meaning |
| --- | --- |
| `pass` | Meets the preset purpose with no beta-blocking defect. |
| `review` | Usable direction, but needs tuning notes or reviewer judgment. |
| `fail` | Fails the preset purpose or introduces material artifacts. |
| `blocked` | Cannot be evaluated in the required lane yet. |
| `pending` | Not reviewed yet. |

## Review Dimensions

Use the benchmark pack dimensions consistently:

- `identity_preservation`
- `skin_realism`
- `eye_detail`
- `hair_detail`
- `lighting_coherence`
- `background_cleanliness`
- `prompt_or_instruction_adherence`
- `artifact_absence`

## Current Preset Matrix

| Preset | Case id | Evidence lane | Required model | Status | Review focus | Watchouts |
| --- | --- | --- | --- | --- | --- | --- |
| Headshot Cleanup | `edit-001-headshot-cleanup` | `qwen-acceptance` | `qwen-image-edit-2511` | blocked | `identity_preservation`, `skin_realism`, `hair_detail`, `artifact_absence` | waxy skin; hairline drift; cleanup spill into background |
| Natural Skin Retouch | `edit-001-headshot-cleanup` | `qwen-acceptance` | `qwen-image-edit-2511` | pending | `identity_preservation`, `skin_realism`, `eye_detail`, `artifact_absence` | plastic skin; flattened facial structure; under-eye cleanup erases texture |
| Natural Skin Retouch | `edit-002-studio-relight` | `qwen-acceptance` | `qwen-image-edit-2511` | pending | `identity_preservation`, `skin_realism`, `eye_detail`, `artifact_absence` | closest-case coverage only, not exact skin-retouch coverage |
| Studio Relight | `edit-002-studio-relight` | `qwen-acceptance` | `qwen-image-edit-2511` | pending | `identity_preservation`, `lighting_coherence`, `skin_realism`, `eye_detail` | conflicting light direction; over-brightened skin; lost eye contrast |
| Studio Relight | `ref-001-softbox-relight` | `qwen-acceptance` | `qwen-image-edit-2511` | pending | `identity_preservation`, `lighting_coherence`, `skin_realism`, `eye_detail` | reference lighting overpowers identity or skin realism |
| Background Simplify | `edit-003-background-simplify` | `qwen-acceptance` | `qwen-image-edit-2511` | pending | `identity_preservation`, `background_cleanliness`, `hair_detail`, `artifact_absence` | hair-edge tearing; cutout feel; background smear near shoulders |
| Fashion Portrait | `ref-002-editorial-look-transfer` | `qwen-acceptance` | `qwen-image-edit-2511` | pending | `identity_preservation`, `skin_realism`, `lighting_coherence`, `prompt_or_instruction_adherence` | editorial styling drifts identity; airbrushed skin; color grade breaks lighting |
| Fashion Portrait | `edit-002-studio-relight` | `qwen-acceptance` | `qwen-image-edit-2511` | pending | `identity_preservation`, `skin_realism`, `lighting_coherence`, `prompt_or_instruction_adherence` | secondary proxy only; not a one-to-one fashion case |
| Multi-Angle Portrait | `ref-003-pose-and-crop-guidance` | `qwen-acceptance` | `qwen-image-edit-2511` | pending | `identity_preservation`, `prompt_or_instruction_adherence`, `artifact_absence`, `lighting_coherence` | facial drift; warped anatomy; background perspective breaks |
| Multi-Angle Portrait | `ref-001-softbox-relight` | `qwen-acceptance` | `qwen-image-edit-2511` | pending | `identity_preservation`, `prompt_or_instruction_adherence`, `artifact_absence`, `lighting_coherence` | secondary reference-guidance check only |

## Existing Evidence

| Item | Status | Evidence lane | Notes |
| --- | --- | --- | --- |
| Headshot Cleanup / `edit-001-headshot-cleanup` local Qwen attempt | blocked | `blocked-local` | Local CPU-only Windows path exited with `0xC0000005`; this blocks local Qwen signoff. |
| FLUX draft smoke edit | review | `flux-draft` | Completed through app job layer in about 34.7 minutes and reached `pending_review`; useful for reveal/reuse flow, not Qwen quality signoff. |
| FLUX draft smoke rerun | review | `flux-draft` | Approved run on 2026-06-03 completed in about 39.7 minutes and reached `pending_review` with pending image `6ea3269b9814425fa91ab6bdf149b01a`. |
| WR3-007 reveal/reuse scratch validation | pass | `local-product-flow` | Scratch DB copy validated reveal promotion, reusable succeeded run visibility, pending-run removal, and image retrieval for job `dfc36b9bde8d4ee7b111c5196d8ecb24`; real DB stayed `pending_review`. |
| Recent runs reveal/reuse live validation | pass | `local-product-flow` | Scratch DB validation showed reveal, output rendering, `Edit this`, `Download`, composer library reuse, and landing library reuse. |

## Review Procedure

1. Confirm the target evidence lane before running anything.
2. For `qwen-acceptance`, run only on off-box hardware or an environment that is explicitly approved for the heavy run.
3. Record the exact model id, case id, seed, base asset, reference asset if any, and reviewer.
4. Score only the mapped dimensions for the preset/case pair.
5. Write one dominant issue even when the outcome is `pass`; use `none` only when no meaningful issue exists.
6. Do not change preset defaults from one result. Require either a repeated defect or a clear product-level reason.

## Review Log Template

| Date | Preset | Case id | Lane | Model | Outcome | Dominant issue | Decision | Reviewer notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-05-20 | Headshot Cleanup | `edit-001-headshot-cleanup` | `blocked-local` | `qwen-image-edit-2511` | blocked | native CPU-only Windows crash | keep Qwen signoff off-box | Existing local attempts cannot support acceptance review. |
| 2026-05-20 | FLUX draft smoke | `flux-draft-smoke` | `flux-draft` | `flux2-klein-9b-gguf` | review | slow CPU runtime | use for workflow evidence only | Reached `pending_review`; reveal/reuse validated separately. |
| 2026-06-03 | FLUX draft smoke | `local-flux-one-image-smoke` | `flux-draft` | `flux2-klein-9b-gguf` | review | slow CPU runtime; pending manual reveal | record as draft evidence only | Approved run `dfc36b9bde8d4ee7b111c5196d8ecb24` reached `pending_review` after 2387s with pending image `6ea3269b9814425fa91ab6bdf149b01a`; reveal/reuse is not yet validated for this specific run. |
| 2026-06-04 | WR3-007 reveal/reuse check | `local-flux-one-image-smoke` | `local-product-flow` | `flux2-klein-9b-gguf` | pass | none in scratch reveal path | real DB left pending; live reveal remains a user decision | Scratch copy reveal returned image `6ea3269b9814425fa91ab6bdf149b01a`, set job to `succeeded`, moved output to `output_image_id`, cleared `pending_output_image_id`, removed the run from `pending_review`, exposed it in `succeeded`, and returned `/api/images` 200. |

## Coverage Gaps

- `Natural Skin Retouch` still uses nearest-case coverage rather than a dedicated skin-retouch case.
- `Fashion Portrait` still uses editorial/style transfer and relight proxy cases.
- No final Qwen edit acceptance outputs are available from this machine.
- FLUX draft evidence can keep UX work moving, but cannot close the preset quality gate.

## Next Review Actions

1. Decide whether to reveal the real WR3-007 pending output in the live benchmark DB, or keep it pending as a fixture.
2. Keep local FLUX review explicitly labeled as `flux-draft`; do not promote it to Qwen acceptance.
3. Prepare off-box Qwen review for `Headshot Cleanup` first because it is the primary crash-blocked case.
4. After one off-box pass, decide whether to keep current defaults, tune one preset, or add benchmark-pack cases
   for the current coverage gaps.
