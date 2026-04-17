# Fast-Check Runbook

## Purpose

`fast-check` exists to keep CPU-only development practical without lowering the final quality bar.

## Profiles

- backend: `backend/.env.fast-check`
- frontend: `frontend/.env.fast-check`

## Current backend fast-check defaults

- local inference mode
- separate SQLite database
- `cpu-low` profile
- `512x512`
- low-step draft defaults
- one active engine at a time

## When to use fast-check

- frontend integration work
- API and queue validation
- job-event and SSE checks
- preset and prompt direction checks
- replay/history flow checks

## When not to use fast-check

- final quality decisions
- milestone sign-off
- release candidate approval

## Recommended ladder

### Smoke

- `384-512px`
- `4-8` steps
- purpose: correctness

### Draft

- `512-640px`
- `8-12` steps
- purpose: product iteration

### Acceptance

- `768px`
- `16-24` steps
- purpose: quality validation

## Operational note

The fast-check profile is a developer productivity tool. It is not a substitute for acceptance validation.
