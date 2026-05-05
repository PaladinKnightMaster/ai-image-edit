# Preset Benchmark Review

## Purpose

This note maps the Sprint 2 portrait presets to the active `benchmark-pack-v0` cases so tuning and
checkpoint review stay anchored to the same fixed assets, seeds, and evaluation dimensions.

Source of truth:

- preset metadata: `frontend/app/chat/edit-presets.ts`
- benchmark pack guide: `docs/testing/benchmark-pack.md`
- benchmark manifest: `docs/testing/benchmark-pack.v0.json`

## Review rules

- use `Draft` for day-to-day prompt or preset tuning
- use `Acceptance` only for milestone-quality review
- run only the affected preset's primary case set during normal iteration
- when a preset depends on reference guidance, include the mapped reference-guided case in review
- record only meaningful deltas: pass, review, fail, and the dominant failure mode

## Prerequisites

Before starting a real preset review, confirm all of the following:

- local fixture images exist under `fixtures/private/benchmark-pack-v0/`
- filenames match the asset ids in `docs/testing/benchmark-pack.v0.json`
- the backend is running in `main` mode rather than the `fast-check` smoke lane
- `qwen-image-edit-2511` is present and available as the primary edit model
- the reviewer is using the current Sprint 2 UI flow with explicit `Base image` and optional `Reference image`
- the user has explicitly approved the heavy model run after being told about the likely CPU and memory cost

Use `scripts/run_edit_benchmark_case.ps1` as the approval-gated review entrypoint:

- run it without `-RunApproved` first to show the selected benchmark target(s) and the resource warning
- rerun it with `-RunApproved` only after the user explicitly approves the model execution
- the wrapper keeps the real upload/job flow inside one long-lived harness so the model can stay loaded across cases

## Current workspace staging

On 2026-04-20, this workspace staged a temporary proxy fixture pack under
`fixtures/private/benchmark-pack-v0/` by copying existing local generated outputs from `data/images/`.

Proxy mapping:

- `portrait-base-01-studio-headshot.png` <- `bb88ff6829294b4c99123fc55ddda4df.png`
- `portrait-base-02-window-light-three-quarter.png` <- `e3843008470b46fc90a1cf5c2698fa0d.png`
- `portrait-base-03-outdoor-city-walkup.png` <- `11d9364bd5a04d17ad255f55d89199fa.png`
- `reference-lighting-01-softbox.png` <- `19e3c6fa68724673b65481d815bbea87.png`
- `reference-style-02-editorial-cool.png` <- `2a43a65392af4919b3c7fe187caf9e1f.png`
- `reference-pose-03-three-quarter.png` <- `19e3c6fa68724673b65481d815bbea87.png`

Use this staged pack only for draft-tier directional review.

Do not treat it as acceptance-signoff evidence, because these are workspace-local stand-ins rather
than curated benchmark portraits and references.

## Current measured runtime blocker

The first exact-coverage attempt was made on 2026-04-20 against:

- preset: `Headshot Cleanup`
- case: `edit-001-headshot-cleanup`
- model: `qwen-image-edit-2511`
- base upload id: `ca52c383dc934645bea77ffaa2e66a44`
- job id: `1bd31854f83a4c968b9a2c43a12c1df2`

Observed result:

- upload succeeded
- edit job submission succeeded
- the job entered `running`
- the local CPU-only execution remained in model-load / early-run state for more than 6 minutes
- no `output_image_id` was written before the bounded review harness had to stop

Implication:

- the benchmark review path is now wired correctly enough to reach real execution
- the next attempt should run from a long-lived backend session rather than a bounded one-shot shell command
- this is a runtime-throughput issue, not a request-shape or missing-asset issue

On 2026-04-27, the same `Headshot Cleanup` case was rerun with the hardened approval-gated harness and
produced more precise failure evidence:

- job id: `c56ceeaaacd8449fa8066d0c2f2b8a51`
- uploaded base image id: `17860769a1a04d8e96add303c62b80b0`
- the run progressed deeper into pipeline load than the first attempt and kept polling for about 104 seconds
- the Python process then exited with `wrapper_exit_code = -1073741819`
- that exit code maps to `0xC0000005`, a native Windows access violation
- the summary artifact remained on disk with `runner_status = process_exit`, `wrapper_exit_hex = 0xC0000005`, and no `output_image_id`

Implication of the second attempt:

- this is no longer just a slow CPU-only timeout story
- the edit runner is reaching native library code and crashing before it can report a terminal job status
- treat further preset review on this machine as blocked until the runtime path changes
- the next decision is infrastructure-focused: lower-memory execution path, different runtime build, or a stronger machine

## First-pass order

Run the first review pass in this order:

1. `Headshot Cleanup`
2. `Studio Relight`
3. `Background Simplify`
4. `Multi-Angle Portrait`

These presets have direct benchmark-case coverage and should be reviewed before the proxy-coverage
presets (`Natural Skin Retouch` and `Fashion Portrait`).

## Preset matrix

### Headshot Cleanup

- primary cases: `edit-001-headshot-cleanup`
- review focus: `identity_preservation`, `skin_realism`, `hair_detail`, `artifact_absence`
- watchouts: waxy skin, hairline drift, cleanup spill into the background

### Natural Skin Retouch

- primary cases: `edit-001-headshot-cleanup`
- secondary cases: `edit-002-studio-relight`
- review focus: `identity_preservation`, `skin_realism`, `eye_detail`, `artifact_absence`
- watchouts: plastic skin, flattened facial structure, under-eye cleanup that erases texture
- note: `benchmark-pack-v0` does not yet have a skin-retouch-only case, so this preset currently uses
  the closest portrait-edit coverage

### Studio Relight

- primary cases: `edit-002-studio-relight`, `ref-001-softbox-relight`
- review focus: `identity_preservation`, `lighting_coherence`, `skin_realism`, `eye_detail`
- watchouts: lighting from conflicting directions, over-brightened skin, lost eye contrast

### Background Simplify

- primary cases: `edit-003-background-simplify`
- review focus: `identity_preservation`, `background_cleanliness`, `hair_detail`, `artifact_absence`
- watchouts: hair-edge tearing, cutout feel, background smear near shoulders

### Fashion Portrait

- primary cases: `ref-002-editorial-look-transfer`
- secondary cases: `edit-002-studio-relight`
- review focus: `identity_preservation`, `skin_realism`, `lighting_coherence`, `prompt_or_instruction_adherence`
- watchouts: editorial styling that drifts identity, airbrushed skin, color grading that breaks believable lighting
- note: `benchmark-pack-v0` treats this as the nearest editorial proxy rather than a one-to-one fashion preset case

### Multi-Angle Portrait

- primary cases: `ref-003-pose-and-crop-guidance`
- secondary cases: `ref-001-softbox-relight`
- review focus: `identity_preservation`, `prompt_or_instruction_adherence`, `artifact_absence`, `lighting_coherence`
- watchouts: facial drift, warped anatomy, background perspective breaks

## Coverage gap to watch

`Natural Skin Retouch` and `Fashion Portrait` currently rely on nearest-case coverage rather than
exact one-to-one benchmark cases.

If either preset keeps drifting in ways that the mapped cases fail to expose, add a dedicated
benchmark case in the next benchmark-pack version instead of stretching `v0` further.

## Review worksheet

Use this template when recording the first pass:

| Preset | Case id | Tier | Outcome | Dominant issue | Notes |
| --- | --- | --- | --- | --- | --- |
| Headshot Cleanup | `edit-001-headshot-cleanup` | Draft | blocked | Native process crash during CPU-only model load or early execution | First attempt timed out while still in early-run state. Second attempt exited with `0xC0000005` after about 104s, leaving the job `running` with no output image. |
| Studio Relight | `edit-002-studio-relight` | Draft | pending | - | - |
| Studio Relight | `ref-001-softbox-relight` | Draft | pending | - | - |
| Background Simplify | `edit-003-background-simplify` | Draft | pending | - | - |
| Multi-Angle Portrait | `ref-003-pose-and-crop-guidance` | Draft | pending | - | - |
