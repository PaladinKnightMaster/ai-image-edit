# Target Clean-Machine Smoke Operator Packet

Status: Ready for operator execution
Last updated: 2026-06-11
Sprint: Sprint 4
Related ticket: WR4-004
Required before: draft-lane tester invite

## Purpose

Use this packet on the target beta machine to collect the remaining release-smoke evidence for Sprint 4.

This is a non-model smoke. It must not submit an edit job, run Qwen acceptance, or load an inference model.

## Target Commit

Run the latest committed checkout that contains this packet. Record the actual target commit before running:

```powershell
git rev-parse --short HEAD
```

Minimum baseline before this packet was prepared:

```text
634e164
```

If the target machine is on a different commit, keep going only if the checkout includes
`docs/testing/target-clean-machine-smoke-operator-packet.md`, then record the actual commit in the result
block below before running the smoke.

## Operator Preconditions

Confirm these before running:

- installation completed using `docs/setup/windows-draft-lane-beta-install.md`
- repository is cloned on the target beta machine
- dependencies are installed or restored
- `backend/.env.fast-check` exists
- frontend dependencies are installed
- no model run has been approved for this packet
- tester invite is still blocked until this result is recorded

## Primary Command

From repo root:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\scripts\release_smoke.ps1
```

This runs:

- backend fast-check startup smoke
- frontend lint
- frontend typecheck
- frontend production build

## Python Runtime Fallback

If the primary command fails before backend checks because Python cannot be resolved, set target-machine
runtime overrides and rerun the same smoke:

```powershell
$env:AI_IMAGE_EDIT_PYTHON = "C:\Path\To\python.exe"
$env:AI_IMAGE_EDIT_PYTHON_SITE_PACKAGES = "D:\Path\To\ai-image-edit\backend\.venv\Lib\site-packages;D:\Path\To\ai-image-edit\.venv\Lib\site-packages"
powershell.exe -ExecutionPolicy Bypass -File .\scripts\release_smoke.ps1
```

Record both the failed direct attempt and the override rerun in the result block.

## Pass Criteria

Pass requires:

- backend fast-check startup smoke exits 0
- frontend lint exits 0
- frontend typecheck exits 0
- frontend build exits 0

A Windows ESLint cache `EPERM` warning after successful build output is a warning, not an automatic failure,
if `npm.cmd run build` exits 0.

## Failure Handling

| Failure | Owner | Action |
| --- | --- | --- |
| Python runtime cannot resolve | DevOps | Set `AI_IMAGE_EDIT_PYTHON` and `AI_IMAGE_EDIT_PYTHON_SITE_PACKAGES`, then rerun. |
| Backend smoke fails | Backend | Capture terminal output and inspect `backend/.env.fast-check`. |
| Frontend lint or typecheck fails | Frontend | Capture terminal output and block tester invite. |
| Frontend build fails | Frontend + DevOps | Capture terminal output and block tester invite. |

## Result Block To Return

Paste this back to the Commander after the target-machine run:

```text
Target clean-machine smoke result
Date:
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

## Recording Rule

After the operator returns the result, update `docs/testing/clean-machine-release-smoke.md` and
`docs/planning/sprint-4-release-checklist-and-risk-register.md` before any tester invite.
