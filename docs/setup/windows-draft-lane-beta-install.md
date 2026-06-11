# Windows Draft-Lane Beta Installation Guide

Status: Ready for first clean-machine trial
Last updated: 2026-06-11
Scope: Windows local draft-lane closed beta
Owner: DevOps + Tech Lead

## Purpose

Use this guide to install and configure the project on a clean Windows tester machine.

This guide prepares the local edit-first workflow and FLUX draft lane. It does not approve a model run,
provide final Qwen acceptance, or authorize public-beta use.

After installation, run:

1. `docs/testing/target-clean-machine-smoke-operator-packet.md`
2. `docs/testing/draft-lane-beta-tester-handoff.md`
3. `docs/testing/draft-lane-beta-session-runbook.md`

## Supported Beta Boundary

This installation supports:

- local Windows operation
- edit-first workflow testing
- FLUX through the Windows sd-cli path
- manual-review reveal behavior
- compare, download, and result reuse

It does not support or claim:

- final `qwen-image-edit-2511` acceptance
- hosted GPU execution
- masking or batch editing
- mobile workflows
- public-beta readiness

## 1. Machine Requirements

Verified project baseline:

- Windows 11 x64
- Python 3.12.x; current workspace was created with Python 3.12.10
- Node.js 18.17 or newer; Node 20 or 22 LTS is recommended for a tester machine
- npm included with Node.js
- Git for Windows
- PowerShell 5.1 or newer

Storage:

- reserve at least 35 GB free for the draft-lane model assets, dependencies, caches, and generated files
- 45 GB free is recommended when downloading rather than transferring a prepared asset pack
- the current workspace FLUX asset tree is about 29 GB because it contains optional encoder variants

Memory:

- setup and non-model smoke do not establish an inference RAM minimum
- FLUX CPU inference is hardware-dependent and can take tens of minutes
- 32 GB RAM is an operational recommendation for a draft-run machine, not an acceptance guarantee

Network:

- internet is required for clone, dependency installation, and asset download
- after dependencies and model assets are present, the app can run with `OFFLINE_MODE=1`

## 2. Install Prerequisites

Install:

- Git for Windows
- Python 3.12 x64, including the `py` launcher
- Node.js 20 or 22 LTS

Open a new PowerShell window and verify:

```powershell
git --version
py -3.12 --version
node --version
npm.cmd --version
```

Stop if any command is missing.

## 3. Clone And Pin The Repo

Choose a local path with enough disk space:

```powershell
cd D:\
git clone https://github.com/PaladinKnightMaster/ai-image-edit.git
cd .\ai-image-edit
```

Checkout the commit approved by the Commander. Record the actual commit:

```powershell
$ApprovedCommit = "PASTE_APPROVED_COMMIT_HERE"
git checkout $ApprovedCommit
git rev-parse --short HEAD
git status --short
```

The working tree should be clean before installation begins.

Do not copy `.venv`, `frontend\node_modules`, or generated `data` files from another machine.

## 4. Install Backend Dependencies

Use one repo-root virtual environment:

```powershell
py -3.12 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r .\backend\requirements.txt
```

The requirements include a Git-based dependency, so Git must remain available during installation.

Verify the backend imports:

```powershell
& .\.venv\Scripts\python.exe -c "import fastapi, uvicorn, dotenv; print('backend imports ok')"
```

Activation is not required for normal backend startup because the repo launcher resolves `.venv`.

## 5. Install Frontend Dependencies

The repo includes `frontend\package-lock.json`, so use `npm.cmd ci`:

```powershell
Push-Location .\frontend
npm.cmd ci
Copy-Item .env.example .env.local
Pop-Location
```

Keep this value in `frontend\.env.local`:

```text
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

Use `npm.cmd`, not `npm`, when PowerShell script-shim policy blocks `npm.ps1`.

## 6. Create The Draft-Lane Backend Environment

Create the local environment file:

```powershell
Copy-Item .\backend\.env.example .\backend\.env
notepad .\backend\.env
```

Set or replace these values:

```text
APP_COMMIT=PASTE_APPROVED_COMMIT_HERE
FRONTEND_ORIGIN=http://localhost:3000
OFFLINE_MODE=1
DB_PATH=./data/app.beta.db
MAX_WIDTH=512
MAX_HEIGHT=512
MAX_STEPS=12
MAX_CONCURRENT_JOBS=1
INFERENCE_MODE=local
WARMUP_MODELS=0
SAFETY_REVIEW_MODE=manual
QUALITY_PROFILE=cpu-low
ENABLED_MODELS=flux2-klein-9b-gguf
DEFAULT_WIDTH=512
DEFAULT_HEIGHT=512
DEFAULT_STEPS=8
FLUX2_USE_PY_BINDINGS=0
FLUX2_USE_SDCLI_FALLBACK=1
FLUX2_SDCLI_PATH=tools\sdcli\master-474-61659ef\avx2\sd-cli.exe
FLUX2_DIFFUSION_GGUF=./models/flux2_klein_9b_gguf/diffusion_model/flux-2-klein-9b-Q4_K_M.gguf
FLUX2_VAE=./models/flux2_klein_9b_gguf/vae/flux2-vae.safetensors
FLUX2_LLM_GGUF=./models/flux2_klein_9b_gguf/text_encoder_gguf/Qwen3-8B-Q6_K.gguf
FLUX2_DEFAULT_STEPS=8
FLUX2_DEFAULT_GUIDANCE=4.0
FLUX2_DEFAULT_SIZE=512
FLUX2_DEFAULT_STRENGTH=0.6
```

Keep `SAFETY_REVIEW_MODE=manual`. FLUX outputs must remain behind the reveal gate before normal reuse.

## 7. Provision FLUX And sd-cli Assets

The model and tool directories are ignored by Git. A normal clone does not contain them.

Choose one provisioning method.

### Option A: Transfer A Prepared Asset Pack

Copy these directories from a trusted prepared machine:

```text
models\flux2_klein_9b_gguf\
tools\sdcli\
```

Do not transfer `.venv`, `node_modules`, databases, or generated tester images.

### Option B: Download On The Target Machine

The download helper resolves `python` from the active shell, so activate the new venv for this step:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
& .\.venv\Scripts\Activate.ps1
powershell.exe -ExecutionPolicy Bypass -File .\scripts\fetch_flux2_klein_gguf.ps1
powershell.exe -ExecutionPolicy Bypass -File .\scripts\fetch_sdcli.ps1 -Variant avx2
python .\scripts\verify_flux2_klein_assets.py
python .\scripts\diagnose_flux2_sdcli.py
deactivate
```

If the CPU does not support AVX2, use `-Variant avx` or `-Variant noavx` and update
`FLUX2_SDCLI_PATH` in `backend\.env` to the path printed by the download script.

Model downloads may require a Hugging Face token or additional Hub tooling. Complete all downloads before
disconnecting the machine from the network.

FLUX assets are draft-lane, non-commercial evidence in this project. Keep manual review enabled and confirm
the applicable model licenses before any use outside the private beta evaluation.

## 8. Validate Installation Without Running A Model

Run the required non-model release smoke:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\scripts\release_smoke.ps1
```

If the launcher cannot resolve Python, use:

```powershell
$env:AI_IMAGE_EDIT_PYTHON = (Resolve-Path .\.venv\Scripts\python.exe).Path
$env:AI_IMAGE_EDIT_PYTHON_SITE_PACKAGES = (Resolve-Path .\.venv\Lib\site-packages).Path
powershell.exe -ExecutionPolicy Bypass -File .\scripts\release_smoke.ps1
```

Pass requires:

- backend fast-check smoke exits 0
- frontend lint exits 0
- frontend typecheck exits 0
- frontend build exits 0

Record the result using `docs/testing/target-clean-machine-smoke-operator-packet.md`.

## 9. Start The App

Backend terminal:

```powershell
cd D:\Path\To\ai-image-edit
powershell.exe -ExecutionPolicy Bypass -File .\scripts\start_backend.ps1 -Mode main -NoReload
```

Frontend terminal:

```powershell
cd D:\Path\To\ai-image-edit\frontend
npm.cmd run dev
```

Open:

```text
http://localhost:3000/chat
```

Use `localhost`, not `127.0.0.1`, because the default backend CORS origin is
`http://localhost:3000`.

## 10. Verify Health And Model Registration

With both services running:

```powershell
Invoke-RestMethod http://localhost:8000/health
Invoke-RestMethod http://localhost:8000/ready
Invoke-RestMethod http://localhost:8000/api/models
```

Expected:

- `/health` reports `ok`
- `/ready` responds without a server error
- `/api/models` includes `flux2-klein-9b-gguf`
- the FLUX model is reported as present when the configured assets and sd-cli path are valid

This verification does not run inference.

## 11. First Tester Session Boundary

Do not submit the first edit job during installation.

Before any model execution:

- receive explicit approval for the run
- confirm the tester understands FLUX is draft-lane evidence only
- confirm CPU inference can take tens of minutes
- keep `SAFETY_REVIEW_MODE=manual`
- follow `docs/testing/draft-lane-beta-session-runbook.md`

## 12. Common Windows Failures

| Problem | Action |
| --- | --- |
| `Activate.ps1` is blocked | Use `Set-ExecutionPolicy -Scope Process Bypass`, or call `.venv\Scripts\python.exe` directly. |
| `npm.ps1` is blocked | Use `npm.cmd`. |
| Python launcher points to an old install | Delete `.venv`, recreate it with `py -3.12 -m venv .venv`, and reinstall requirements. |
| Backend launcher cannot resolve Python | Set `AI_IMAGE_EDIT_PYTHON` and `AI_IMAGE_EDIT_PYTHON_SITE_PACKAGES` as shown above. |
| FLUX model is missing | Recheck asset paths and run `verify_flux2_klein_assets.py`. |
| sd-cli is missing | Run `fetch_sdcli.ps1` and update `FLUX2_SDCLI_PATH`. |
| Browser cannot call backend | Use `http://localhost:3000`, confirm backend port 8000, and check `FRONTEND_ORIGIN`. |
| Port 3000 or 8000 is busy | Stop the conflicting process before the tester session. |
| Build prints ESLint cache `EPERM` | Treat as a warning only when the build exits 0 after successful output. |

## 13. Update Procedure

Before updating, stop backend and frontend.

```powershell
git fetch origin
$ApprovedCommit = "PASTE_APPROVED_COMMIT_HERE"
git checkout $ApprovedCommit
& .\.venv\Scripts\python.exe -m pip install -r .\backend\requirements.txt
Push-Location .\frontend
npm.cmd ci
Pop-Location
powershell.exe -ExecutionPolicy Bypass -File .\scripts\release_smoke.ps1
```

Do not overwrite `backend\.env`, `frontend\.env.local`, model assets, or tester data without an explicit
migration or reset decision.

## 14. Installation Record

Record this before tester handoff:

```text
Install date:
Machine label:
Windows version:
CPU:
RAM:
Free disk before install:
Repo path:
Commit:
Python version:
Node version:
npm version:
Git version:
Asset provisioning method:
FLUX asset verification:
sd-cli diagnostics:
Release smoke result:
Warnings:
Blockers:
Operator:
```

Installation is complete only when the non-model release smoke is recorded and no unassigned blocker
remains.
