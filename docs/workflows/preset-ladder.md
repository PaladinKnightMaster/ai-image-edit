# Preset Ladder

## Purpose

This project uses a three-tier preset ladder so CPU-only development stays practical without blurring
the difference between correctness checks and milestone-quality review.

The ladder vocabulary is the shared contract across backend envs, frontend preset labels, docs, and
manual validation.

## The three tiers

### Smoke

- purpose: correctness, crash detection, queue/event checks, API and UI validation
- target range: `384-512px`, `4-8` steps
- expected use: short local checks before or during implementation
- frontend label: `Smoke`

### Draft

- purpose: normal product iteration, prompt tuning, replay/history validation, compare rough quality
- target range: `512px`, `8-12` steps on the CPU-only development machine
- expected use: the default daily working lane
- frontend label: `Draft`

### Acceptance

- purpose: milestone-quality review and benchmark comparison
- target range: `768px`, `16-24` steps for the main Qwen lane
- expected use: only at checkpoints, not as the normal edit loop
- frontend label: `Acceptance`

## Current environment mapping

- `backend/.env.fast-check`
  - the draft lane
  - `QUALITY_PROFILE=cpu-low`
  - defaults: `512x512`, `8` steps
  - limits: up to `512x512`, `12` steps
- `backend/.env`
  - the main local validation lane
  - `QUALITY_PROFILE=cpu-balanced`
  - defaults: `768x768`, `20` steps

## Current frontend mapping

- `Smoke`
  - Qwen: `512x512`, `8` steps
  - FLUX: `512x512`, `4` steps
- `Draft`
  - Qwen: `512x512`, `12` steps
  - FLUX: `512x512`, `8` steps
- `Acceptance`
  - Qwen: `768x768`, `20` steps
  - FLUX: `768x768`, `12` steps

FLUX remains an optional advanced lane in Sprint 1, so its acceptance preset is only for bounded
manual checks, not for broad release sign-off.

## Rules

- use `Smoke` for correctness, not for aesthetic judgment
- use `Draft` as the default day-to-day iteration lane
- use `Acceptance` only when the result is being reviewed as a quality checkpoint
- do not silently raise fast-check defaults beyond the draft lane without updating this doc and the
  runbook
