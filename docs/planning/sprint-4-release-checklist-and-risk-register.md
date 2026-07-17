# Sprint 4 Release Checklist and Risk Register

Status: Reviewable
Last updated: 2026-07-16
Sprint: Sprint 4
Ticket: WR4-007
Owner: Tech Lead + DevOps

## Release Verdict

Draft-lane closed beta preparation is conditionally allowed.

Do not start a final Qwen-acceptance beta or public beta from the current evidence. The tester handoff can
move to owner review, but actual tester use still requires isolated clean-Windows smoke evidence and explicit
scope wording from `docs/planning/beta-scope-decision.md`.

Windows Sandbox surrogate evidence is accepted for this Sprint 4 gate because no fresh physical machine is
available. It must be labeled as surrogate evidence and does not prove independent-machine compatibility.

## Scope Boundary

Allowed:

- local edit-first workflow validation
- setup and launch validation
- reveal, compare, download, and reuse behavior
- base image plus optional reference-image workflow clarity
- FLUX local draft-lane behavior as draft evidence only

Not allowed:

- final `qwen-image-edit-2511` quality claims
- acceptance-tier portrait preset claims
- hosted GPU execution
- new engine families
- masking, batch editing, mobile work, or broad preset expansion

## Release Gate Checklist

| Gate | Required evidence | Current state | Owner | Release status |
| --- | --- | --- | --- | --- |
| Beta scope lock | `docs/planning/beta-scope-decision.md` | Complete; draft-lane beta prep only | Tech Lead + Product | Pass |
| Target-machine installation guide | `docs/setup/windows-draft-lane-beta-install.md` | Prepared; first clean-machine trial pending | DevOps + Tech Lead | Pass for preparation |
| Off-box Qwen packet | `docs/testing/off-box-qwen-acceptance-packet.md` | Prepared; execution not started | AI/ML + Infra | Pass for draft-lane beta; blocker for Qwen beta |
| Off-box Qwen acceptance result | `data/qwen-acceptance-summary.json`, `data/qwen-acceptance.db`, worksheet rows | Missing | AI/ML | Not required for draft-lane beta; required for Qwen beta |
| Current workspace release smoke | `docs/testing/clean-machine-release-smoke.md` | Passed at commit `e676d9a` with Python override and noted build warning | DevOps | Pass as local evidence |
| Isolated clean-Windows smoke | Windows Sandbox or physical target run using `docs/testing/target-clean-machine-smoke-operator-packet.md`, recorded in `docs/testing/target-clean-machine-smoke-result-log.md` | `e829507` package prepared; post-restart host Sandbox app still crashes before bootstrap | DevOps + host owner | Blocked; repair/reset pending; required before tester handoff unless owner accepts residual risk |
| Tester handoff | `docs/testing/draft-lane-beta-tester-handoff.md` | Owner-reviewed; gated by target clean-machine smoke | Product + Tech Lead | Conditional pass |
| Tester session runbook | `docs/testing/draft-lane-beta-session-runbook.md` | Prepared; first controlled session pending | Product + Tech Lead | Pass for preparation |
| Tester limitations | `docs/testing/beta-tester-limitations-handoff.md` | Owner-reviewed; gated by target clean-machine smoke | Product | Conditional pass |
| Pending-review reveal/reuse | Scratch-copy reveal validation and backend/API tests | Pass; live WR3-007 fixture intentionally remains pending | Backend + Frontend | Pass |
| WR3-007 fixture decision | `docs/planning/wr3-007-fixture-decision.md` | Complete; live fixture preserved | Tech Lead | Pass |
| Preset quality worksheet | `docs/testing/preset-quality-review-worksheet.md` | Draft and local FLUX evidence mapped; Qwen acceptance pending | AI/ML + Product | Partial |
| Runtime support notes | Current docs and tester handoff limitations | CPU latency and restart behavior documented | Tech Lead + Support | Conditional pass |

## Required Before Any Draft-Lane Tester Session

1. Run the isolated clean-Windows release smoke and record the result in
   `docs/testing/clean-machine-release-smoke.md`.
2. Confirm the invite/session copy includes the required draft-lane boundary:
   "This beta validates the local edit-first workflow and draft-lane behavior; final Qwen edit-quality
   acceptance is still pending off-box validation."
3. Confirm no tester task asks for final Qwen quality evaluation.
4. Keep live job `dfc36b9bde8d4ee7b111c5196d8ecb24` pending unless the fixture decision changes explicitly.
5. Record tester session result rows in `docs/testing/draft-lane-beta-tester-handoff.md`.
6. Operate the session using `docs/testing/draft-lane-beta-session-runbook.md`.

## Risk Register

| ID | Risk | Severity | Status | Owner | Mitigation / next action |
| --- | --- | --- | --- | --- | --- |
| R1 | Final Qwen edit acceptance is missing. | High | Open | AI/ML + Infra | Keep Qwen beta and public beta no-go until off-box packet results are recorded. |
| R2 | Isolated clean-Windows release smoke cannot start because Sandbox app 0.8.107.0 is missing `WinRT.Runtime 2.2.0.0`. | High | Reproduced after host restart; smoke not executed | DevOps + host owner | Repair Sandbox in Windows Settings and retry; reset and retry if repair fails. |
| R3 | Tester may confuse FLUX draft output with final Qwen quality. | High | Mitigated for handoff | Product + Tech Lead | Use the required wording boundary in every tester session and invite. |
| R4 | CPU-only edit runs can take tens of minutes. | Medium | Open | Product + Support | Frame beta around workflow and available draft results; warn before any model execution. |
| R5 | Queued/running jobs fail on backend restart. | Medium | Known limitation | Backend | Keep restart behavior in support notes; do not promise durable replay queue. |
| R6 | Pending-review outputs can be misused if reveal is bypassed. | Medium | Mitigated | Backend + Frontend | Keep reveal/reuse tests green and preserve WR3-007 as a pending fixture for regression checks. |
| R7 | Windows Python/venv launcher mismatch can block setup. | Medium | Confirmed locally; mitigated with override | DevOps | Use `AI_IMAGE_EDIT_PYTHON` and `AI_IMAGE_EDIT_PYTHON_SITE_PACKAGES` overrides when needed. |
| R8 | Preset quality evidence is partial and partly proxy-based. | Medium | Open | AI/ML + Product | Label local FLUX results as draft evidence; require Qwen acceptance worksheet rows for acceptance claims. |
| R9 | Frontend build can emit Windows ESLint cache warnings. | Low | Known issue | Frontend + DevOps | Treat as warning only if build exits 0; record if it appears on target machine. |
| R10 | Sandbox does not prove independent physical-machine compatibility. | Medium | Accepted residual risk | Release Guard | Label evidence as surrogate and revisit when another machine becomes available. |

## Evidence Commands

Required release smoke:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\scripts\release_smoke.ps1
```

Off-box Qwen preview only:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\scripts\run_edit_benchmark_case.ps1 `
  -PresetRun headshot-cleanup,studio-relight,background-simplify,softbox-relight,editorial-look-transfer,multi-angle-portrait `
  -DotenvPath .\backend\.env `
  -ModelRoot .\models\hf `
  -DbPath .\data\qwen-acceptance.db `
  -SummaryPath .\data\qwen-acceptance-summary.json
```

Do not add `-RunApproved` unless the reviewer explicitly approves the heavy off-box model run.

## Next Owner Actions

| Priority | Action | Owner | Output |
| --- | --- | --- | --- |
| P0 | Repair/reset Sandbox, retry, and record the prepared package before tester invite | DevOps + host owner | Operator result block labeled `Windows Sandbox surrogate`, or an owner acceptance of the recorded blocker |
| P0 | Run the first controlled tester session after smoke passes | Product + Session Operator | Returned `docs/testing/draft-lane-beta-session-runbook.md` result block |
| P1 | Decide whether to execute off-box Qwen acceptance | AI/ML + Product | Acceptance run result or explicit deferral |
| P1 | Prepare tester session result log | Product | Filled tester result rows after any session |

## Sprint 4 Exit Readiness

Sprint 4 can close as a draft-lane beta-prep sprint when:

- isolated clean-Windows smoke is passed or has an owner-assigned blocker
- tester handoff is owner-reviewed
- Qwen acceptance is either recorded off-box or explicitly excluded from beta scope
- all high risks above have an owner and next action
- no new engine or editing surface is added as a release dependency
