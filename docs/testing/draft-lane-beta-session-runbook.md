# Draft-Lane Beta Session Runbook

Status: Ready for first controlled session
Last updated: 2026-07-16
Sprint: Sprint 4
Scope: Private Windows draft-lane beta
Owner: Product + Tech Lead + Session Operator

## Purpose

Use this runbook to operate one controlled draft-lane beta session after the target machine is installed
and its non-model smoke has passed.

This session evaluates the edit-first workflow, setup clarity, status communication, manual reveal,
compare, download, and reuse. It does not provide final Qwen acceptance or public-beta evidence.

## Required Source Documents

Before the session, use:

- installation: `docs/setup/windows-draft-lane-beta-install.md`
- target smoke: `docs/testing/target-clean-machine-smoke-operator-packet.md`
- tester wording: `docs/testing/draft-lane-beta-tester-handoff.md`
- limitations: `docs/testing/beta-tester-limitations-handoff.md`
- release gates: `docs/planning/sprint-4-release-checklist-and-risk-register.md`

## Roles

- Session operator: launches services, verifies health, enforces approval gates, and records evidence.
- Tester: performs the workflow without implementation guidance unless blocked.
- Commander or product owner: approves any new model execution and accepts or assigns blockers.

One person may hold multiple roles, but the session record must identify who approved model execution.

## Session Modes

Choose exactly one mode before the tester starts.

### Mode A: Existing-Result Review

Use when the target machine already has a suitable draft result or pending-review output.

- no new model execution
- tester evaluates reveal, compare, download, and reuse where the available state permits
- preferred when validating workflow without paying inference cost

### Mode B: One Approved FLUX Draft Run

Use only after explicit approval for one local FLUX draft edit.

- one base image
- one preset or direct instruction
- one submitted draft edit job
- no Qwen edit run
- no extra rerun unless separately approved
- CPU execution may take tens of minutes

If approval is not available, do not click the run action. Complete only the preflight and record the
session as blocked before inference.

## 1. Pre-Session Gate

The operator must confirm:

- target installation record is complete
- isolated clean-Windows smoke result is recorded or an owner-assigned blocker is explicitly accepted
- repo commit is approved for the session
- `backend\.env` uses `DB_PATH=./data/app.beta.db`
- `ENABLED_MODELS=flux2-klein-9b-gguf`
- `SAFETY_REVIEW_MODE=manual`
- FLUX and sd-cli diagnostics passed
- tester received the draft-lane limitations
- tester image use is authorized for this private local session
- session mode is selected
- Mode B approval is recorded before launch or explicitly marked pending

Do not use the preserved WR3-007 benchmark fixture as tester data. It remains a project regression fixture.

## 2. Create The Session Record

Before launching services, capture:

```text
Session id:
Date:
Operator:
Tester:
Machine label:
Repo path:
Commit:
Session mode: existing-result / one-approved-flux-run
Model execution approved: yes/no/not-required
Approved by:
Approval time:
Base image source:
Tester consent confirmed: yes/no
Target smoke result:
Known blocker accepted:
```

Do not store personal details beyond what is necessary for the private test record.

## 3. Launch The Backend

Open PowerShell terminal 1:

```powershell
cd D:\Path\To\ai-image-edit
git rev-parse --short HEAD
powershell.exe -ExecutionPolicy Bypass -File .\scripts\start_backend.ps1 -Mode main -NoReload
```

If Python cannot be resolved:

```powershell
$env:AI_IMAGE_EDIT_PYTHON = (Resolve-Path .\.venv\Scripts\python.exe).Path
$env:AI_IMAGE_EDIT_PYTHON_SITE_PACKAGES = (Resolve-Path .\.venv\Lib\site-packages).Path
powershell.exe -ExecutionPolicy Bypass -File .\scripts\start_backend.ps1 -Mode main -NoReload
```

Keep the backend terminal visible to the operator.

## 4. Launch The Frontend

Open PowerShell terminal 2:

```powershell
cd D:\Path\To\ai-image-edit\frontend
npm.cmd run dev
```

Open:

```text
http://localhost:3000/chat
```

Do not use `http://127.0.0.1:3000`; the default backend CORS origin is `http://localhost:3000`.

## 5. Operator Health Check

Open PowerShell terminal 3:

```powershell
Invoke-RestMethod http://localhost:8000/health
Invoke-RestMethod http://localhost:8000/ready
$Models = Invoke-RestMethod http://localhost:8000/api/models
$Models | ConvertTo-Json -Depth 6
```

Confirm:

- `/health` reports `ok`
- `/ready` responds without a server error
- `flux2-klein-9b-gguf` is listed
- the FLUX model reports `present: true`
- the browser loads `/chat` without a backend connection error

Stop the session before tester activity if any required check fails.

## 6. Tester Briefing

Read or paraphrase this boundary:

> This session validates the local edit-first workflow and draft-lane behavior. Local FLUX output is
> draft evidence only. Final Qwen edit-quality acceptance is still pending off-box validation.

Also tell the tester:

- `Edit Photo` is the primary workflow
- the base image is the identity/source image
- a reference image is optional and may not be available for the active model
- CPU inference may take tens of minutes
- a completed FLUX result may require `Reveal` before compare, download, or reuse
- queued or running work is not resumable after backend restart

Do not explain where controls are unless the tester is blocked. Record where assistance was required.

## 7. Baseline Tester Task

Ask the tester to:

1. Open `Edit Photo`.
2. Add one authorized base portrait.
3. Choose the portrait preset that best matches the intended edit, or write one direct instruction.
4. Explain what they expect the edit to change.
5. Continue according to the selected session mode.

Do not require a reference image in the baseline task.

## 8. Mode A Procedure: Existing Result

If using an existing result:

1. Open Recent runs or the output library.
2. If an approved pending-review output is available, ask the tester to reveal it.
3. Ask the tester to find before/after comparison.
4. Ask the tester to download the result.
5. Ask the tester to reuse the result as the next base image.
6. Stop before submitting another job.

Record any missing state. Do not manufacture or reveal the WR3-007 regression fixture for a tester session.

## 9. Mode B Approval Checkpoint

Immediately before submission, the operator must record:

```text
Model: flux2-klein-9b-gguf
Lane: local FLUX draft
Submission count authorized: 1
Base image authorized: yes/no
Prompt or preset reviewed: yes/no
Expected runtime disclosed: yes/no
Manual review enabled: yes/no
Explicit approval received: yes/no
Approved by:
Approval time:
```

If `Explicit approval received` is not `yes`, stop. Do not submit the job.

## 10. Mode B Procedure: One FLUX Draft

After approval:

1. Ask the tester to submit the edit once.
2. Record the submission time.
3. Observe whether queued/running status is understandable without giving an ETA.
4. Do not refresh, restart the backend, or submit another job while it runs.
5. Record the final status: `pending_review`, `succeeded`, or `failed`.
6. If `pending_review`, ask the tester to use `Reveal`.
7. Ask the tester to compare before and after.
8. Ask the tester to download the result.
9. Ask the tester to reuse the revealed result as the next base image.
10. Stop before submitting the reused image unless another run is separately approved.

Capture job id, run id, output image id or pending output image id, elapsed time, and any error shown.

## 11. Optional Reference-Image Check

Run this only if the active UI/model metadata exposes a reference-image slot.

Ask the tester to:

1. identify which image is the base identity/source image
2. identify the reference as visual guidance only
3. describe whether the distinction is clear

Do not submit a reference-guided job unless it is separately approved and the active model supports it.

## 12. Operator Observation Checklist

Record whether the tester:

- found `Edit Photo` without prompting
- understood base image versus optional reference image
- understood preset wording
- understood queued/running status
- understood the reveal gate
- found compare
- found download
- found reuse
- confused FLUX draft evidence with final model quality
- interpreted CPU latency as final product performance
- needed operator assistance

## 13. Tester Questions

Ask:

1. Did `Edit Photo` feel like the obvious starting point?
2. Was the base image versus reference image distinction clear?
3. Did the selected preset or instruction match your expectation?
4. Did job status feel trustworthy during the wait?
5. Did the reveal step make sense?
6. Could you find compare, download, and reuse?
7. Where did the workflow feel slow, unclear, or risky?
8. Did any copy imply final quality when it should have said draft or beta?
9. What would need to change before you trusted a final quality-focused beta?

## 14. Session Result

Use one result:

- `pass`: baseline workflow completed without a beta-blocking defect
- `pass_with_notes`: workflow completed with non-blocking confusion or warnings
- `blocked`: setup, health, approval, or environment prevented the workflow
- `failed`: a beta-blocking product defect occurred after the session started

Record:

```text
Session result:
Start time:
End time:
Model run submitted: yes/no
Submission count:
Job id:
Run id:
Final job status:
Output or pending image id:
Elapsed time:
Reveal completed:
Compare completed:
Download completed:
Reuse completed:
Reference-image check completed:
Main blocker:
Owner:
Tester summary:
Operator notes:
Follow-up decision:
```

## 15. Evidence Handling

- Keep the session local unless the tester approved sharing specific artifacts.
- Do not commit tester images, generated images, local databases, or private fixtures to Git.
- Store only the minimum session metadata needed for Sprint 4 review.
- Record durable conclusions in `docs/testing/draft-lane-beta-tester-handoff.md` or a dedicated approved
  session evidence file.
- Keep FLUX output labeled `flux-draft`; never relabel it as Qwen acceptance.

## 16. Shutdown

After evidence is recorded:

1. Stop the frontend with `Ctrl+C` in terminal 2.
2. Stop the backend with `Ctrl+C` in terminal 1.
3. Confirm no job is queued or running before closing the backend.
4. Close the browser.
5. Leave `data\app.beta.db` and `data\images\` intact until the session record is reviewed.

Do not delete tester data during the session. Any cleanup requires an explicit retention decision.

## 17. Result Block To Return

Paste this back to the Commander:

```text
Draft-lane beta session result
Date:
Session id:
Operator:
Tester label:
Machine:
Commit:
Session mode:
Target smoke result:
Model execution approved:
Approved by:
Model run submitted:
Job id:
Run id:
Final status:
Elapsed time:
Reveal:
Compare:
Download:
Reuse:
Result:
Main blocker:
Owner:
Warnings:
Tester summary:
Operator notes:
```

No tester invite or additional model run is implied by completing this runbook.
