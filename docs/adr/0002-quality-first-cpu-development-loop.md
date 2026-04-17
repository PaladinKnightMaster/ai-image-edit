# ADR 0002: Quality-First CPU Development Loop

- Status: Accepted
- Date: 2026-04-17

## Context

The primary development machine is CPU-only. Full Qwen inference runs can take hours, which makes real-model validation too slow for the normal development loop.

At the same time, product quality remains the governing objective. The project cannot let "fast" local settings become the only source of truth.

## Decision

Use a tiered development and validation ladder:

- `smoke` for API, queue, and UI correctness
- `draft` for normal iteration and product tuning
- `acceptance` for milestone quality validation

Daily development uses `backend/.env.fast-check` and the matching frontend fast-check profile. Acceptance-quality runs happen only at checkpoints.

## Why

- It preserves quality as the primary objective.
- It keeps CPU-only development viable.
- It prevents slow full-model runs from blocking all implementation work.
- It creates a shared vocabulary for test intensity across backend, frontend, and AI/ML work.

## Consequences

- The repo needs explicit benchmark fixtures and acceptance gates.
- CI should focus on smoke-level checks, not slow inference.
- Preview and final quality should be treated as separate modes in both engineering and product design.

## Non-goals

- This does not lower the final quality bar.
- This does not replace acceptance validation with low-step previews.
