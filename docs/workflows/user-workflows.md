# User Workflows

Status: Active; cancellation and retry extensions are planned
Last updated: 2026-07-16
Owner: Product + UX Reviewer

## 1. Edit Photo

1. choose `Edit Photo`
2. upload or reuse a base image
3. optionally add one visual reference image
4. choose a portrait preset or write an instruction
5. confirm bounded settings
6. submit the edit
7. monitor queued/running state
8. reveal the result when manual review is required
9. compare before and after
10. refine, download, or reuse the result

## 2. Create From Scratch

1. choose `Create from Scratch`
2. write a prompt
3. submit a draft generation
4. review or reveal the result
5. select `Edit this`
6. continue in Edit Photo with the generated result as the base image

## 3. Reference-Guided Edit

The base image remains the identity and source. The optional reference supplies visual guidance for lighting,
style, framing, or angle; it is not presented as a replacement identity.

## 4. Manual Review

1. generation completes as `pending_review`
2. result remains excluded from normal reuse
3. user chooses reveal
4. backend promotes the pending image to the visible output
5. job becomes `succeeded`
6. output becomes available for compare, download, and reuse

## 5. History And Retry

Current behavior:

- history and output library can stage successful output as a new edit base
- replay creates a new run instead of mutating old evidence

Planned Sprint 5 behavior:

- eligible failed or interrupted jobs expose `Retry`
- retry uses the same request snapshot and creates a new attempt
- deterministic failures explain why automatic retry is unavailable

## 6. Cancellation

Planned Sprint 5 behavior:

1. user requests cancel
2. backend persists `cancel_requested`
3. UI shows shutdown in progress
4. executor cooperatively stops or terminates its child process
5. temporary output is cleaned
6. job becomes `cancelled`

Closing the page does not cancel a job.

## 7. Disconnect And Recovery

1. browser loses the EventSource connection
2. UI shows reconnecting instead of failed
3. UI fetches persisted job state
4. terminal backend state is rendered immediately
5. non-terminal state reconnects with bounded backoff

After backend restart, current behavior marks queued/running jobs failed. Sprint 5 will replace this with explicit
attempt, interrupted, and retry policy where feasible. No mid-step model resume is promised.

## 8. CPU Expectation

Model runs can take tens of minutes. The UI must not promise a fixed ETA. It should show queue position, last
activity, stage/progress when real, and clear cancel/retry choices.
