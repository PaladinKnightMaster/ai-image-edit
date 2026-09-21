# Target Clean-Machine Smoke Result Log

Status: Awaiting first isolated clean-Windows result
Last updated: 2026-07-16
Sprint: Sprint 4
Related ticket: WR4-004
Owner: DevOps + Tech Lead

## Purpose

Use this log to record an isolated Windows non-model release smoke result returned from
`docs/testing/target-clean-machine-smoke-operator-packet.md`. A physical target machine is preferred, but a
Windows Sandbox surrogate is accepted for Sprint 4 because no separate fresh machine is currently available.

This log is evidence intake only. It does not authorize a model run, submit an edit job, or change the
Qwen acceptance status.

## Recording Rule

Before any draft-lane tester session, record either:

- an isolated clean-Windows smoke pass, or
- a blocker with an assigned owner and an explicit decision that the tester session may proceed despite it.

If neither exists, tester invite and tester session remain blocked.

## Required Returned Fields

Paste or summarize the operator result block with these fields:

```text
Isolated clean-Windows smoke result
Date:
Evidence class: physical target machine / Windows Sandbox surrogate
Machine/environment:
Repo path:
Commit:
Primary command result:
Python override used: yes/no
Backend fast-check smoke:
Frontend lint:
Frontend typecheck:
Frontend build:
Warnings:
Blockers:
Owner assignment if blocked:
Terminal summary:
```

## Pass Criteria

The target smoke is a pass only when all required checks exit successfully:

- backend fast-check smoke
- frontend lint
- frontend typecheck
- frontend production build

A Windows ESLint cache `EPERM` warning is acceptable only if the frontend build exits 0.

## Current Result Entries

| Date | Evidence class | Machine/environment | Commit | Result | Python override | Warnings | Blockers | Owner | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-07-16 | Windows Sandbox surrogate | Windows 10 Pro 25H2 build 26200.8655; Sandbox app 0.8.107.0 | `e829507` | blocked before bootstrap | n/a | First launch installed/updated the Sandbox app | `WindowsSandboxRemoteSession.exe` crashed because `WinRT.Runtime, Version=2.2.0.0` was missing; no mapped evidence files were created | DevOps + host owner | Restart the host, retry the same immutable package, then repair/reset Sandbox if the crash persists. No model ran. |
| 2026-07-17 | Windows Sandbox surrogate | Post-restart retry; Sandbox app 0.8.107.0 | `e829507` | blocked before bootstrap | n/a | Host restart completed | Identical missing `WinRT.Runtime, Version=2.2.0.0` crash; all-users package inspection also denied by host permissions | Host owner | Use Windows Settings to repair Sandbox, retry, then reset and retry if repair fails. No model ran. |
| 2026-07-17 | Windows Sandbox surrogate | Post-repair retry; Sandbox app 0.8.107.0 | `e829507` | blocked before bootstrap | n/a | Windows Settings Repair completed | Identical missing `WinRT.Runtime, Version=2.2.0.0` crash at 12:11:07 PM; mapped output remained empty | Host owner | Reset Windows Sandbox in Settings, then retry the same package once. No model ran. |
| 2026-07-17 | Windows Sandbox surrogate | Post-reset retry; Sandbox app 0.8.107.0 | `e829507` | blocked before bootstrap | n/a | Windows Settings Reset completed | Identical missing `WinRT.Runtime, Version=2.2.0.0` crash at 12:18:33 PM; mapped output remained empty | Host owner + Release Guard | Choose owner acceptance of the persistent blocker or explicitly approve optional-feature reinstall and restarts. No model ran. |

## 2026-07-16 Blocker Detail

- source package: `.artifacts/windows-sandbox-smoke/20260716T234119Z-e829507/`
- source archive commit: `e829507b551c3ec8e362359c4d1f8e1df7b79b6b`
- source archive SHA-256: `6dff9c31fad646e0c687b3c5dd12d31e7debc5a73bf40de5884062819d66839a`
- package validation: passed; host worktree clean; three installers had valid Authenticode signatures
- launch attempt 1: Windows Update installed `MicrosoftWindows.WindowsSandbox` app version `0.8.107.0`
- launch attempt 2: remote-session process crashed before the mapped bootstrap started
- event evidence: .NET Runtime event 1026, Application Error event 1000, and Windows Error Reporting event 1001
- exception: `System.IO.FileNotFoundException` for `WinRT.Runtime, Version=2.2.0.0`
- bootstrap transcript/result: absent because the Sandbox VM did not reach `LogonCommand`
- model execution: none

## 2026-07-17 Post-Restart Retry

- unchanged package and source commit: `e829507`
- launch time: approximately 12:02 PM America/New_York
- result: Sandbox client exited before bootstrap; mapped output remained empty
- event evidence: .NET Runtime event 1026, Application Error event 1000, Windows Error Reporting event 1001
- repeated exception: `System.IO.FileNotFoundException` for `WinRT.Runtime, Version=2.2.0.0`
- package process: `WindowsSandboxRemoteSession.exe` version `0.8.107.0`
- permission boundary: `Get-AppxPackage -AllUsers` and `Get-AppxProvisionedPackage -Online` were denied
- next action: host owner uses Windows Settings to repair the Windows Sandbox system component, then retries the
  same immutable `.wsb`; reset only if repair does not fix startup
- model execution: none

## 2026-07-17 Post-Repair Retry

- unchanged package and source commit: `e829507`
- launch time: approximately 12:11 PM America/New_York
- prerequisite: host owner completed Windows Settings Repair
- result: Sandbox client exited before bootstrap; mapped output remained empty
- repeated exception: `System.IO.FileNotFoundException` for `WinRT.Runtime, Version=2.2.0.0`
- event evidence: .NET Runtime 1026 at 12:11:07 PM, Application Error 1000, Windows Error Reporting 1001
- next action: host owner resets the Windows Sandbox system component, then retries the same immutable `.wsb` once
- model execution: none

## 2026-07-17 Post-Reset Retry

- unchanged package and source commit: `e829507`
- launch time: approximately 12:18 PM America/New_York
- prerequisite: host owner completed Windows Settings Reset
- result: Sandbox client exited before bootstrap; mapped output remained empty
- repeated exception: `System.IO.FileNotFoundException` for `WinRT.Runtime, Version=2.2.0.0`
- event evidence: .NET Runtime 1026 at 12:18:33 PM, Application Error 1000, Windows Error Reporting 1001
- recovery ladder exhausted: restart, Repair, and Reset all reproduced the same host-app failure
- owner decision required: accept the persistent external blocker for Sprint 4 entry-gate purposes, or explicitly
  approve optional-feature disable/re-enable plus required host restarts
- model execution: none

## Follow-Up After A Pass

After the first isolated clean-Windows pass:

1. update the table above with the actual result
2. update `docs/testing/clean-machine-release-smoke.md`
3. update `docs/planning/sprint-4-release-checklist-and-risk-register.md`
4. proceed to `docs/testing/draft-lane-beta-session-runbook.md`

## Follow-Up After A Blocker

After a blocker:

1. preserve the failed command summary
2. assign an owner
3. decide whether the blocker stops tester handoff
4. update the release checklist risk register
5. do not start a model run as part of this smoke unless separately approved
