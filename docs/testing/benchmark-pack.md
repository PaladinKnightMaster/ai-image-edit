# Benchmark Pack

## Purpose

The benchmark pack gives the team a stable way to evaluate quality over time without relying on ad hoc prompts.

## Pack structure

Create a fixed set with:

- 3 text-to-image prompts
- 3 portrait edit prompts
- 3 reference-guided edit prompts
- fixed seeds where applicable

## Evaluation dimensions

- identity preservation
- skin realism
- eye detail
- hair detail
- lighting coherence
- background cleanliness
- prompt adherence

## Use by tier

### Draft

- use smaller sizes and lower steps
- confirm directional quality only

### Acceptance

- use the agreed acceptance profile
- compare against prior accepted outputs when available
- record findings in sprint or release notes

## Suggested initial benchmark cases

### T2I

1. natural studio portrait
2. cinematic environmental portrait
3. clean product-photo style portrait setup

### Edit

1. headshot cleanup, keep identity
2. studio relight, realistic skin
3. background simplify, preserve subject realism

### Reference-guided edit

1. base portrait + lighting reference
2. base portrait + style reference
3. generated draft + reference-guided refinement

## Rule

Do not change the benchmark pack casually. If the pack changes, record why in planning or decision docs so trend comparisons remain meaningful.
