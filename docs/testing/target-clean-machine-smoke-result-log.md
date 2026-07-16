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
| pending | Windows Sandbox surrogate | isolated Windows environment | pending | pending | pending | pending | harness implemented; isolated smoke not yet run | DevOps | Required before tester handoff unless owner explicitly accepts the blocker. |

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
