# Frontend Architecture

## Scope

This document captures the current frontend shape and the architectural direction implied by the roadmap.

## Current route structure

- `/` -> redirects to `/chat`
- `/chat` -> main product shell
- `/arena` -> backend-health placeholder page

## Current implementation shape

The frontend is highly concentrated in `frontend/app/chat/page.tsx`.

That page currently owns:

- backend/system loading
- readiness loading
- model loading
- recent and failed runs
- local thread history persistence
- attachment upload and history attachment selection
- submit flow for generation and editing
- SSE subscription and progress state
- reveal handling
- export and cleanup controls
- settings and CPU presets

## Current state model

State is mostly local component state plus browser persistence:

- local component state for runtime view state
- `localStorage` for thread history and model preference
- server-derived state for models, runs, system, and job status

There is no explicit app-level product mode yet. The page currently infers mode from whether attachments exist.

## Architectural issues

- one oversized page is carrying too many responsibilities
- product mode is inferred rather than declared
- history, cleanup, and maintenance actions live beside core creation/editing actions
- visible copy still reflects arena/chat positioning rather than edit-first positioning

## Intended architectural direction

The roadmap implies a shell that is organized around workflows instead of one monolithic chat surface.

Recommended top-level frontend boundaries:

- editor shell
- mode switcher
- prompt and preset composer
- source image panel
- result viewer and compare view
- history and replay surface
- advanced settings drawer

## Current responsibility split

- frontend owns workflow orchestration and UI state
- backend owns job execution, system state, storage, and runner constraints

That split is acceptable, but the frontend needs clearer boundaries internally.

## Documentation follow-up

- UI structure: `docs/design/ui-information-architecture.md`
- user flows: `docs/workflows/user-workflows.md`
- testing expectations: `docs/testing/test-strategy.md`
