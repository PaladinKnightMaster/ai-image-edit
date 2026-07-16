# Frontend Architecture

Status: Active
Last updated: 2026-07-16
Owner: Frontend Lead

## Routes

- `/` redirects to `/chat`
- `/chat` is the main edit-first product shell
- `/arena` is secondary diagnostics

## Current Component Shape

`frontend/app/chat/page.tsx` is the stateful coordinator. Extracted components include:

- `ModeSwitchHero`
- `WorkflowLandingState`
- `ComposerPanel`
- `MessageTimeline`
- `BeforeAfterCompare`
- `HistoryPickerModal`
- `UtilitiesPanel`

Structured preset metadata lives in `frontend/app/chat/edit-presets.ts`; shared presentation types and status copy
have separate modules.

## Current State Ownership

- local React state: active workflow, form settings, attachments, messages, and loading state
- browser persistence: thread history and model preference in `localStorage`
- backend state: models, readiness, jobs, runs, images, and persisted progress
- transport: `fetch` for commands and snapshots, EventSource for live job events

## Current Strengths

- edit/create mode is explicit
- base/reference roles are explicit
- output reuse preserves edit context
- pending-review outputs are gated before reuse
- compare, download, retry presentation, history, and maintenance surfaces exist

## Current Risks

- `page.tsx` still owns API calls, EventSource lifecycle, persistence, and most orchestration
- the EventSource `error` channel can conflate transport failure with a server job failure event
- full message state is synchronously serialized to `localStorage` on frequent updates
- smooth timeline scrolling can run during progress updates
- silent fetch failures can leave stale UI without a clear backend-connection state
- no automated frontend flow suite protects the primary workflows

## Target Boundaries

Introduce these boundaries only when their Sprint 5 behavior is implemented:

- `api-client`: typed HTTP commands and snapshot reads
- `job-stream-controller`: reconnect, reconciliation, backoff, and terminal-state handling
- `thread-store`: versioned, debounced persistence with large blobs outside synchronous `localStorage`
- `job-command` hooks: submit, cancel, retry, reveal
- focused workflow components that consume stable props rather than backend wire formats

## Transport Rule

A browser disconnect is an observer problem, not proof of job failure. On EventSource failure:

1. show reconnecting/disconnected state
2. query `GET /api/jobs/{job_id}`
3. apply persisted backend state
4. reconnect only when the job remains non-terminal
5. mark failed only when the backend reports `failed`

## Service Worker Rule

A Service Worker may later cache versioned static application assets. It must not own model execution, durable
job state, cancellation, retry, or recovery. The Python backend and orchestration layer remain authoritative.

## Verification

- lint, typecheck, and production build
- component/state unit tests where useful
- Playwright flows against deterministic non-model states
- live browser validation only after automated coverage exists
