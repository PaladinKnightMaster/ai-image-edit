# Draft-Lane Beta Tester Handoff

Status: Owner-reviewed; gated by isolated clean-Windows smoke
Last updated: 2026-07-16
Sprint: Sprint 4
Ticket: WR4-005

## Purpose

This is the tester-facing handoff for a limited draft-lane closed beta. It is aligned to
`docs/planning/beta-scope-decision.md`.

The session operator should run the workflow through
`docs/testing/draft-lane-beta-session-runbook.md`.

Do not use this as a final Qwen-quality beta invite. This beta validates local workflow, setup, reveal,
reuse, and draft-lane behavior only. Tester access remains blocked until isolated clean-Windows smoke is
passed or an owner-assigned blocker is accepted.

## One-Sentence Scope Boundary

This beta validates the local edit-first workflow and draft-lane behavior; final Qwen edit-quality
acceptance is still pending off-box validation and should not be judged from local FLUX draft outputs.

## Invite Copy

You are invited to test a private local portrait-editing workflow.

This beta focuses on whether the product flow is understandable and useful:

- start with `Edit Photo`
- add a base portrait
- optionally add one reference image
- choose a preset or write an edit instruction
- review the result
- reveal manual-review outputs when needed
- compare, download, or reuse a result

Important limitation: this beta does not validate final Qwen edit quality. Local FLUX outputs are
draft-lane evidence only, and CPU-only runs can take a long time.

## Tester Setup Notes

Before a tester session:

- confirm installation completed using `docs/setup/windows-draft-lane-beta-install.md`
- confirm the isolated Windows environment passed the clean-machine release smoke runbook
- confirm the session is using `http://localhost:3000/chat`
- confirm the tester knows this is local/offline-after-setup workflow testing
- confirm no hosted GPU, masking, batch editing, final Qwen acceptance, or mobile workflow is expected
- confirm whether the session will review existing draft results or run a new draft edit
- confirm any new model execution has explicit approval before it starts

## Tester Task Script

Ask the tester to complete these tasks in order:

1. Open `/chat` and start from `Edit Photo`.
2. Add one base portrait.
3. Choose one portrait preset that matches the desired edit.
4. Review an available draft result, or run a new draft edit only if the session owner approved model execution.
5. If the output is hidden behind manual review, use `Reveal`.
6. Compare before and after.
7. Download the result.
8. Reuse the result as the next edit base.
9. Repeat with an optional reference image only if the workflow is available on that machine.

## What To Watch

Observe whether the tester:

- understands that `Edit Photo` is the primary workflow
- understands base image vs reference image
- notices job status and progress without confusion
- understands the reveal gate
- finds compare, download, and reuse actions without prompting
- treats FLUX output quality as draft evidence only
- does not interpret slow CPU runtime as final product performance

## Feedback Questions

Ask these after the session:

1. Did `Edit Photo` feel like the obvious starting point?
2. Was the base image vs reference image distinction clear?
3. Did the reveal step make sense?
4. Could you find compare, download, and reuse actions?
5. Which preset label best matched what you expected?
6. Where did the workflow feel slow, unclear, or risky?
7. Did any copy imply final model quality when it should have said draft or beta?
8. Would you trust this workflow for private local portrait editing if output quality improves?
9. What would need to change before you would trust a final quality-focused beta?

## Known Limitations To Tell Testers

- Final `qwen-image-edit-2511` acceptance is not complete.
- Local FLUX output quality is draft evidence only.
- CPU-only edits can take tens of minutes.
- Running or queued jobs fail on backend restart; there is no durable replay queue yet.
- Manual-review outputs must be revealed before normal reuse.
- Reference images are optional visual guidance, not the identity source.
- Some preset benchmark coverage is still proxy coverage.
- Masking, batch editing, hosted GPU execution, and mobile workflows are out of scope.

## Owner Checklist

Before sending an invite, the owner must confirm:

- beta scope decision is linked
- isolated clean-Windows release smoke is passed or the blocker is explicitly assigned and accepted
- tester limitations are included in the invite or session notes
- Qwen acceptance is not implied
- local FLUX output is described as draft-lane evidence only
- any model execution plan has explicit approval before the tester session starts
- feedback questions are prepared
- tester session result will be recorded in a Sprint 4 evidence artifact
- session operator is using `docs/testing/draft-lane-beta-session-runbook.md`

## Result Logging Template

| Date | Tester | Machine | Scope | Result | Main blocker | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| YYYY-MM-DD | - | - | draft-lane closed beta | pending | - | - |
