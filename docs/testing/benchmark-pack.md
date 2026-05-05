# Benchmark Pack

Version: `v0`
Last updated: 2026-04-19

## Purpose

The benchmark pack gives the team a fixed reference set for quality review so preset tuning and
workflow changes are not judged against ad hoc prompts or random sample images.

`v0` is intentionally small. It exists to unblock Sprint 2 and Sprint 3 work with a stable set of:

- case ids
- fixed seeds
- local fixture asset slots
- evaluation focus areas

## Files

- Human guide: `docs/testing/benchmark-pack.md`
- Machine-readable manifest: `docs/testing/benchmark-pack.v0.json`
- Local asset path convention: `fixtures/README.md`

## Pack contents

The v0 pack contains 9 cases:

- 3 text-to-image cases
- 3 portrait edit cases
- 3 reference-guided edit cases

The pack also defines 6 local fixture asset slots:

- 3 base portrait inputs
- 3 reference inputs

## Asset policy

- Do not commit private portrait or reference images to the repo by default.
- Store local fixture images under `fixtures/private/benchmark-pack-v0/`.
- Filenames must match the asset ids in `docs/testing/benchmark-pack.v0.json`.
- If a fixture image must be replaced, keep the asset id stable only when the replacement is visually
  equivalent. Otherwise bump the benchmark pack version.
- Prefer team-owned QA photos, licensed internal sample images, or explicitly consented portraits.

## Local asset slots

### Base portraits

- `portrait-base-01-studio-headshot.png`
  - adult subject
  - head-and-shoulders crop
  - neutral background
  - sharp eyes and visible hair detail
  - well-exposed, straightforward identity baseline

- `portrait-base-02-window-light-three-quarter.png`
  - adult subject
  - three-quarter angle
  - indoor window light
  - moderate background detail
  - lighting and skin transitions useful for relight checks

- `portrait-base-03-outdoor-city-walkup.png`
  - adult subject
  - outdoor or mixed background
  - visible flyaway hair / edge detail
  - background distractions suitable for simplify cleanup checks

### Reference images

- `reference-lighting-01-softbox.png`
  - clear soft studio lighting direction
  - usable as a relight target

- `reference-style-02-editorial-cool.png`
  - clear cool-toned editorial mood
  - usable as a color and styling reference without changing identity

- `reference-pose-03-three-quarter.png`
  - clear portrait framing / pose feel
  - usable for composition guidance without extreme body changes

## Case list

### Text-to-image

- `t2i-001-natural-studio-headshot`
  - model: `qwen-image-2512`
  - seed: `1101`
  - prompt: `a natural studio headshot of an adult woman, 85mm portrait, soft key light, neutral gray backdrop, realistic skin texture, sharp eyes, detailed hair, photorealistic`
  - negative prompt: `blurry, waxy skin, distorted eyes, extra face, extra limbs, low detail`
  - review focus: skin realism, eye detail, background cleanliness, prompt adherence

- `t2i-002-cinematic-window-portrait`
  - model: `qwen-image-2512`
  - seed: `1102`
  - prompt: `a cinematic portrait of an adult man beside a large window, warm practical lights in the background, natural skin, realistic hair, shallow depth of field, photorealistic`
  - negative prompt: `blurry, plastic skin, malformed hands, duplicate features, low detail`
  - review focus: lighting coherence, facial realism, hair detail, prompt adherence

- `t2i-003-clean-editorial-beauty`
  - model: `qwen-image-2512`
  - seed: `1103`
  - prompt: `a clean editorial beauty portrait of an adult subject, seamless light beige backdrop, balanced studio lighting, realistic skin, crisp eye detail, premium photo finish`
  - negative prompt: `blurry, oversmoothed skin, asymmetrical eyes, warped anatomy, cluttered background`
  - review focus: skin realism, eye detail, premium portrait finish, background cleanliness

### Portrait edit

- `edit-001-headshot-cleanup`
  - model: `qwen-image-edit-2511`
  - base asset: `portrait-base-01-studio-headshot.png`
  - seed: `2101`
  - instruction: `subtle headshot cleanup, reduce minor blemishes and shine, keep pores, keep identity unchanged, preserve hairline and background`
  - review focus: identity preservation, natural skin texture, hairline stability, artifact absence

- `edit-002-studio-relight`
  - model: `qwen-image-edit-2511`
  - base asset: `portrait-base-02-window-light-three-quarter.png`
  - seed: `2102`
  - instruction: `relight into a soft studio key light with gentle fill while keeping skin natural and identity unchanged`
  - review focus: lighting coherence, skin realism, eye detail, identity preservation

- `edit-003-background-simplify`
  - model: `qwen-image-edit-2511`
  - base asset: `portrait-base-03-outdoor-city-walkup.png`
  - seed: `2103`
  - instruction: `simplify the background and reduce distractions while preserving subject realism, hair edges, clothing texture, and facial identity`
  - review focus: background cleanliness, hair edge integrity, identity preservation, artifact absence

### Reference-guided edit

- `ref-001-softbox-relight`
  - model: `qwen-image-edit-2511`
  - base asset: `portrait-base-01-studio-headshot.png`
  - reference asset: `reference-lighting-01-softbox.png`
  - seed: `3101`
  - instruction: `match the softbox lighting direction and softness from the reference while preserving the subject's identity and natural skin texture`
  - review focus: identity preservation, lighting transfer quality, skin realism, artifact absence

- `ref-002-editorial-look-transfer`
  - model: `qwen-image-edit-2511`
  - base asset: `portrait-base-02-window-light-three-quarter.png`
  - reference asset: `reference-style-02-editorial-cool.png`
  - seed: `3102`
  - instruction: `apply the reference mood and cool editorial color palette while keeping facial identity, skin realism, and believable lighting`
  - review focus: reference adherence, identity preservation, color consistency, skin realism

- `ref-003-pose-and-crop-guidance`
  - model: `qwen-image-edit-2511`
  - base asset: `portrait-base-03-outdoor-city-walkup.png`
  - reference asset: `reference-pose-03-three-quarter.png`
  - seed: `3103`
  - instruction: `nudge the portrait toward the reference framing and pose feel without changing identity, creating warped anatomy, or losing background plausibility`
  - review focus: pose/framing adherence, anatomy stability, identity preservation, artifact absence

## Review policy by tier

### Smoke

Smoke does not use this pack. Smoke remains the cheap correctness lane defined in:

- `docs/testing/smoke-validation-path.md`

### Draft

Use draft-tier settings for tuning and directional comparison:

- run only the affected workflow subset when iterating
- prefer 1-3 representative cases instead of the full pack during daily work
- record only meaningful deltas, not every exploratory run

### Acceptance

Use acceptance-tier settings for milestone review:

- run the full currently active pack
- compare against the prior accepted outputs when available
- record pass / review / fail notes per case

## Activation status

- text-to-image cases: active now
- portrait edit cases: active for Sprint 2 preset and edit-flow work
- reference-guided edit cases: active now that the Sprint 2 reference-image workflow has landed

## Evaluation dimensions

Use these dimensions consistently:

- identity preservation
- skin realism
- eye detail
- hair detail
- lighting coherence
- background cleanliness
- prompt or instruction adherence
- artifact absence

## Change control

Do not change prompts, seeds, or fixture asset ids casually.

If the pack changes:

- document why
- version the pack forward
- update Sprint planning docs that depend on it
- avoid mixing results from different pack versions in one quality summary
