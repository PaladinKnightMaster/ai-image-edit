# UI Information Architecture

Status: Active
Last updated: 2026-07-16
Owner: Frontend Lead + UX Reviewer

## Current IA

- `/` redirects to `/chat`
- `/chat` is the primary edit-first workspace
- `/arena` is secondary diagnostics

The main workspace exposes explicit `Edit Photo` and `Create from Scratch` modes. Editing is the default product
direction; creation supports the generate-to-edit bridge.

## Primary Workflow Objects

- base image
- optional reference image
- preset or custom instruction
- model and bounded advanced settings
- job status and progress
- pending or revealed result
- before/after comparison
- run history and output library

## Workspace Structure

### Primary

- mode selection
- source inputs
- preset/instruction composer
- run command and current status
- result timeline and comparison

### Supporting

- output library and history reuse
- download and `Edit this`
- advanced model/settings controls
- collapsed maintenance utilities

### Diagnostics

- backend/model readiness
- storage details
- failed-run cleanup and import/export
- `/arena` status surface

Diagnostics must not compete visually with the primary edit workflow.

## Reliability UX

Long CPU work must expose persisted truth rather than optimistic animation.

- `queued`: waiting for the single local execution slot
- `running`: inference active with last activity and progress where available
- `reconnecting`: browser transport unavailable; job outcome unknown until API reconciliation
- `cancel_requested`: cancellation persisted and executor shutdown in progress
- `interrupted`: worker/lease lost; retry policy required
- `retry_wait`: eligible retry recorded but not yet running
- `pending_review`: output exists but is not reusable until reveal
- `succeeded`, `failed`, `cancelled`: terminal outcomes

Proposed states must not appear in production copy before backend support exists.

## Interaction Rules

- browser close or stream disconnect does not cancel a job
- cancel and retry are explicit commands with visible acknowledgement
- retry preserves source inputs and parameters but creates a new attempt
- pending outputs stay out of normal reuse
- base identity remains distinct from optional visual guidance
- advanced controls remain secondary to preset/instruction workflow

## Performance Rules

- avoid writing large message/blob state synchronously on every progress event
- auto-scroll only when the user is already near the latest result or a new message is added
- reconcile progress without rerendering unrelated controls
- keep static asset caching separate from job execution state

## Target Internal Boundaries

- editor shell
- typed API client
- job stream controller
- versioned thread persistence
- composer
- result/compare surface
- history/output library
- utilities and diagnostics
