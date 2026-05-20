# Beta Tester Limitations Handoff

Last updated: 2026-05-20
Status: Internal draft for future closed-beta handoff

## Purpose

Use this note when preparing a closed-beta tester invite, runbook, or onboarding message. It states what
testers should expect from the current edit-first MVP without overstating model quality or runtime
readiness.

Do not send this as a beta invite yet. The current beta readiness verdict is still `Not beta-ready yet`.

## Current Scope

The current MVP is an edit-first local studio workflow:

1. start with `Edit Photo`
2. add one base image
3. optionally add one reference image when the active model supports it
4. choose a portrait preset or write a direct edit instruction
5. review the result
6. reveal manual-review outputs when required
7. compare, download, or reuse a revealed output for another edit round

`Create from Scratch` remains available as a supporting draft lane, not the main product promise.

## What Testers Can Evaluate

Testers can evaluate:

- whether the edit-first workflow is understandable
- whether base image vs optional reference image is clear
- whether reveal, compare, download, and reuse actions make sense
- whether long-running job status feels trustworthy enough
- whether preset language matches common portrait-editing intent
- whether output-library reuse is understandable after a result is revealed

## What Testers Should Not Treat As Final

Testers should not treat these as final acceptance evidence:

- local `flux2-klein-9b-gguf` output quality
- CPU-only runtime duration on this development machine
- proxy fixture benchmark results
- any Qwen edit quality claim until off-box `qwen-image-edit-2511` validation is recorded

## Known Limitations To Disclose

- The intended Qwen edit acceptance lane is blocked locally on this machine by a native Windows crash during
  CPU-only execution.
- FLUX is currently the local draft edit lane. It is useful for product-flow evidence, but it is not final
  Qwen edit acceptance evidence.
- CPU-only edits can take tens of minutes. The app should be judged on whether progress and recovery feel
  understandable, not on this machine's raw speed.
- If the backend restarts while a job is queued or running, that job is marked failed. There is no durable
  replay queue yet.
- Manual-review outputs can be complete while still hidden from normal reuse. They must be revealed before
  they appear as ordinary reusable outputs.
- Reference images are guidance only. The base image remains the source identity and primary edit input.
- Some preset benchmark coverage is still proxy coverage. `Natural Skin Retouch` and `Fashion Portrait`
  do not yet have exact one-to-one dedicated benchmark cases.
- New editing surfaces such as masking, batch editing, and hosted GPU execution are outside Sprint 3 scope.

## Tester Feedback Prompts

Ask testers to answer these questions after a session:

1. Did `Edit Photo` feel like the obvious starting point?
2. Was the difference between base image and reference image clear?
3. Did the reveal step make sense, or did it feel like hidden state?
4. Could you find how to compare, download, and reuse a result?
5. Which preset label best matched the edit you expected?
6. Where did the workflow feel slow, unclear, or risky?

## Current Go / No-Go Message

Use this status until the beta gate changes:

The product flow is ready for internal dogfooding and structured review. It is not ready for closed beta
until preset quality review and the Qwen edit acceptance lane are resolved or explicitly scoped out.
