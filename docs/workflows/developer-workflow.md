# Developer Workflow

## Purpose

This project should be developed with two separate loops:

- a fast local loop for normal engineering work
- a slower validation loop for real quality checkpoints

## Daily workflow

1. start from `AGENTS.md` and current handoff docs if this is a new AI session
2. use `backend/.env.fast-check` for backend iteration
3. keep one heavy model active at a time
4. use smoke or draft settings for UI and API work
5. reserve slow acceptance runs for milestones

## Normal implementation order

1. read current state and active sprint doc
2. inspect existing code before changing it
3. use the smallest useful war-room mode
4. make code or doc changes
5. run the relevant smoke checks
6. update durable docs if the system understanding changed

## Current practical guardrails

- do not rely on full Qwen runs as the normal feedback loop
- do not expand model/runtime scope while Sprint 1 stabilization is unfinished
- do not treat README alone as the system architecture source of truth

## Expected smoke checks

- backend import and startup
- `/health`
- `/ready`
- `/api/models`
- frontend lint
- frontend typecheck
- frontend production build
- one fast local job smoke where practical

## Frontend validation command set

- `cd frontend && npm run lint`
- `cd frontend && npm run typecheck`
- `cd frontend && npm run build`
- optional combined path: `cd frontend && npm run validate`

## Expected checkpoint validation

- benchmark pack review
- acceptance settings review
- product flow walkthrough
- manual compare of portrait quality dimensions
