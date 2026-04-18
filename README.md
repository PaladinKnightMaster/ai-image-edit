# AI Image Edit (V1)

Offline-first, self-hosted AI image generator/editor oriented around a local studio workflow. The
current build ships a Next.js frontend and FastAPI backend with local-first job flows, health checks,
and Sprint 1 developer tooling for normal vs fast-check operation.

## Repo layout

- `frontend/` Next.js App Router + Tailwind UI
- `backend/` FastAPI service
- `scripts/` model mirroring + smoke utilities
- `data/` local persistence (empty)
- `models/` local model assets + caches

## Current models

Available model IDs (use these in `ENABLED_MODELS` and API requests):
- `qwen-image-2512` (text-to-image)
- `qwen-image-edit-2511` (image editing)
- `flux2-klein-9b-gguf` (text-to-image + edit via stable-diffusion.cpp)
- `sdxl-openvino` (text-to-image via OpenVINO, optional refiner)

`/api/models` marks a model as `present` only when the currently configured runtime path has the
required local assets. Qwen uses mirrored Hugging Face snapshots under `MODEL_ROOT`; FLUX and SDXL
use their own env-configured local asset paths.

## Recent updates (rolling)

- FLUX.2 sd-cli backend supports SSE progress streaming from live stdout parsing.
- UI includes a “CPU Realistic” preset button to auto-fill settings per model.
- Run cleanup endpoints + UI controls for removing recent/failed runs.

## Quickstart

Backend:
1) `python -m venv .venv`
2) Activate the venv
   - Windows PowerShell: `./.venv/Scripts/Activate.ps1`
   - macOS/Linux: `source .venv/bin/activate`
3) `pip install -r backend/requirements.txt` (CPU, requires `git` on PATH)
   - GPU: `pip install -r backend/requirements-gpu.txt` (edit CUDA version if needed)
   - OpenVINO (optional): `pip install -r backend/requirements-openvino.txt`
4) Copy env vars: `copy backend/.env.example backend/.env`
5) Run: `.\scripts\start_backend.ps1 -Mode main`

Frontend:
1) `cd frontend`
2) `npm install`
3) Copy env vars: `copy .env.example .env.local`
4) Run: `cd frontend && npm run dev`
5) Open `http://localhost:3000/chat`

Run both (optional convenience path, default backend env only):
- `make dev`

Windows backend launcher commands:
- Main mode: `.\scripts\start_backend.ps1 -Mode main`
- Fast-check mode: `.\scripts\start_backend.ps1 -Mode fast-check`

Windows backend smoke command:
- `.\scripts\smoke_backend.ps1`

If you do not have GNU Make installed, run these directly:
- Backend: `.\scripts\start_backend.ps1 -Mode main`
- Frontend: `cd frontend && npm run dev`

## Cloning to a new machine (same path notes)

You generally **should not copy `.venv`** across machines. Even with the same OS + Python version,
it can break due to absolute paths and compiled wheels.

If the new machine is truly identical and you **clone to the exact same path**, a copied `.venv`
*may* work, but it is not guaranteed. The reliable approach is always:
1) Recreate the venv on the new machine.
2) Reinstall requirements from `backend/requirements*.txt`.

If you still want to try reusing a venv, make sure:
- OS + architecture match
- Python version matches exactly
- Repo path is identical
- GPU driver + CUDA versions match (if using GPU)

Example (identical path + version):
- OS: Windows 11 x64 on both machines
- Python: 3.12.2 (same installer path, e.g. `C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe`)
- Repo path: `D:\1_PROJECT\PRIVATE_WORK\ai-image-edit`

## Worker mode (optional)

Run inference in a separate process (lower RAM pressure on the API process).

1) In `backend/.env` set:
```
INFERENCE_MODE=worker
WORKER_URL=http://127.0.0.1:8001
WORKER_CALLBACK_URL=http://127.0.0.1:8000
```

2) Start API + worker in separate terminals:
```
# API
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Worker
cd backend
python -m uvicorn worker.main:app --reload --host 0.0.0.0 --port 8001
```

3) Start frontend as usual.

## From scratch (full install + model downloads)

Windows (PowerShell):
```powershell
cd D:\1_PROJECT\PRIVATE_WORK\ai-image-edit
python -m venv .venv
./.venv/Scripts/Activate.ps1
pip install -r backend/requirements.txt
copy backend/.env.example backend/.env
cd frontend
npm install
copy .env.example .env.local
cd ..
```

Linux/macOS (bash):
```bash
cd /path/to/ai-image-edit
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cp backend/.env.example backend/.env
cd frontend
npm install
cp .env.example .env.local
cd ..
```

Download models (Qwen diffusers):
```bash
python scripts/mirror_models.py
```

Download FLUX.2 klein GGUF assets (optional):
```bash
# Windows
powershell -ExecutionPolicy Bypass -File scripts/fetch_flux2_klein_gguf.ps1
# Linux/macOS
bash scripts/fetch_flux2_klein_gguf.sh
python scripts/verify_flux2_klein_assets.py
```

Tips:
- Set `HF_TOKEN` before downloads for higher Hub rate limits.
- To prefetch fp8 text encoder: `FLUX2_TEXT_ENCODER_PRECISION=fp8` or pass `--text-encoder fp8`.

Run dev servers:
```bash
# Backend
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# Frontend (new terminal)
cd frontend
npm run dev
```

GPU setup from scratch (Windows/Linux/macOS):
```bash
# Install GPU-enabled torch (replace cu121 with your CUDA version)
pip install -r backend/requirements-gpu.txt
```
Notes:
- Ensure the CUDA toolkit/drivers match your PyTorch wheel.
- On Windows, use the same venv steps above before installing GPU deps.

## Offline model mirroring

Mirror the required Qwen models to local disk so the backend can run with the network disabled.

1) `python scripts/mirror_models.py`
2) Optional revision pinning: `python scripts/mirror_models.py --revision main`

This writes to `models/hf/<org>/<name>/<revision>/...` and the backend reads from `MODEL_ROOT`.

Smoke-check offline config + model presence (requires `diffusers` installed):
- `python scripts/smoke_offline_load.py`

## FLUX.2 klein GGUF (fast engine)

This optional engine uses stable-diffusion.cpp. It stays fully offline after you mirror assets.

Important: 15-byte files happen when you download VAE/text encoder from the wrong repo (the GGUF repo
does not contain those files and returns `Entry not found`).

1) Download model assets (resumable, uses HF Hub API):
   - Windows: `powershell -ExecutionPolicy Bypass -File scripts/fetch_flux2_klein_gguf.ps1`
   - Linux/macOS: `bash scripts/fetch_flux2_klein_gguf.sh`
   - Optional flags: `--quant Q4_K_M`, `--text-encoder fp8`, `--llm-file Qwen3-8B-Q6_K.gguf`
   - Env override: `FLUX2_TEXT_ENCODER_PRECISION=fp8`
   - For higher Hub limits: set `HF_TOKEN`
   - If you see Xet errors: `pip install hf-xet`
   - Requires: `pip install "huggingface_hub>=0.32.0"`
2) Verify assets:
   - `python scripts/verify_flux2_klein_assets.py`
3) Preferred backend (in-process bindings):
   - `pip install -r backend/requirements-flux.txt`
   - Windows note: pybindings are more stable with a GGUF text encoder. Convert once:
     - `python scripts/convert_flux2_text_encoder.py --precision fp4`
     - Set `FLUX2_TEXT_ENCODER_GGUF=./models/flux2_klein_9b_gguf/text_encoder/qwen_3_8b_fp4mixed.gguf`
   - If pybindings still crash on Windows, enable sd-cli fallback:
     - Set `FLUX2_USE_SDCLI_FALLBACK=1` and follow the sd-cli steps below.
   - Windows default: if `FLUX2_USE_PY_BINDINGS` is unset, the backend defaults to sd-cli.
4) sd-cli fallback (binary):
   - `powershell -ExecutionPolicy Bypass -File scripts/fetch_sdcli.ps1 -Variant avx2`
   - Set `FLUX2_SDCLI_PATH` to the `sd` binary and `FLUX2_LLM_GGUF` to a GGUF LLM.
   - Diagnostics: `python scripts/diagnose_flux2_sdcli.py`
   - Windows guide: `docs/engines/flux2_sdcli_windows.md`

Exact hf download commands (manual alternative):
```bash
hf download unsloth/FLUX.2-klein-9B-GGUF --include "flux-2-klein-9b-Q4_K_M.gguf"
hf download Comfy-Org/flux2-klein-9B --include "split_files/vae/flux2-vae.safetensors"
hf download Comfy-Org/flux2-klein-9B --include "split_files/text_encoders/qwen_3_8b_fp4mixed.safetensors"
# Required for sd-cli (--llm):
hf download Qwen/Qwen3-8B-GGUF --include "Qwen3-8B-Q6_K.gguf"
# FP8 encoder option:
# hf download Comfy-Org/flux2-klein-9B --include "split_files/text_encoders/qwen_3_8b_fp8mixed.safetensors"
```
Copy the downloaded files into:
- `models/flux2_klein_9b_gguf/diffusion_model/`
- `models/flux2_klein_9b_gguf/vae/`
- `models/flux2_klein_9b_gguf/text_encoder/`
- `models/flux2_klein_9b_gguf/text_encoder_gguf/`

Tip: you can download both fp4 and fp8 encoders ahead of time and switch later by setting
`FLUX2_TEXT_ENCODER_PRECISION` in `backend/.env` without re-downloading.

Memory tip: if you only want one model loaded, set `ENABLED_MODELS` to a single id (for example,
`qwen-image-2512`, `flux2-klein-9b-gguf`, or `sdxl-openvino`). Valid IDs are listed under “Current models.”
Only those models are registered, warmed, and shown in the UI.

Manual review gate:
- `SAFETY_REVIEW_MODE=manual` is the default and required for FLUX.2 licensing guidance.
- Jobs return `pending_review` until you call `POST /api/jobs/{job_id}/reveal` (UI exposes a Reveal button).

License note:
- `unsloth/FLUX.2-klein-9B-GGUF` is non-commercial and requires manual review or filters. Keep the manual
  review gate enabled for production use.

## Torch install (CPU vs GPU)

By default, `backend/requirements.txt` pulls the CPU wheel of PyTorch.
For GPU acceleration, use `backend/requirements-gpu.txt` and update the CUDA tag if needed.

Examples (replace `cu121` with your CUDA version):
- CPU: `pip install --index-url https://download.pytorch.org/whl/cpu torch`
- CUDA: `pip install --index-url https://download.pytorch.org/whl/cu121 torch`

## Endpoints

- `GET /health` -> `{ "status": "ok" }`
- `GET /ready` -> `{ "ready": true/false, "status": "...", "details": {...} }`
- `GET /api/version` -> `{ "name": "...", "version": "...", "commit": "dev" }`
- `GET /api/models` -> list of model IDs, capabilities, and local availability
- `POST /api/infer/t2i` -> `{ "image_id": "..." }`
- `POST /api/infer/edit` -> `{ "image_id": "..." }`
- `POST /api/images/upload` -> `{ "image_id": "..." }`
- `GET /api/images/{image_id}/meta` -> returns stored metadata if available
- `GET /api/images/{image_id}` -> returns PNG
- `GET /api/system` -> device info + active quality profile
- `POST /api/jobs/t2i` -> `{ "job_id": "..." }`
- `POST /api/jobs/edit` -> `{ "job_id": "..." }`
- `POST /api/jobs/{job_id}/reveal` -> `{ "image_id": "..." }` (manual review gate)
- `POST /api/jobs/replay` -> `{ "job_id": "..." }`
- `GET /api/jobs/{job_id}` -> job + run metadata
- `GET /api/jobs/{job_id}/events` -> SSE stream
- `GET /api/runs` -> recent runs (supports `status=failed`)
- `DELETE /api/runs/{run_id}` -> remove a run (and its job record). Optional `delete_images=1`.
- `DELETE /api/runs` -> bulk delete runs (supports `status=failed` and/or `limit=...`, optional `delete_images=1`)
- `GET /api/runs/{run_id}/export` -> reproducibility export JSON
- `GET /api/stats` -> queue + latency summary
- `GET /api/diagnostics/engines` -> optional engine diagnostics
- `POST /api/images/generate` -> `{ "job_id": "..." }` (alias for /api/jobs/t2i)
- `POST /api/images/edit` -> `{ "job_id": "..." }` (alias for /api/jobs/edit)

## Environment variables

Backend (`backend/.env.example`):
See `backend/ENV.md` for full descriptions and tuning recipes.
- `APP_NAME` display name for the API
- `APP_VERSION` semantic version string
- `APP_COMMIT` git commit hash or label (defaults to `dev`)
- `FRONTEND_ORIGIN` CORS origin (default `http://localhost:3000`)
- `OFFLINE_MODE` set to `1` to force offline mode (default)
- `MODEL_ROOT` local model root (default `./models/hf`)
- `MODEL_REVISION` optional revision to load (use if you mirrored a specific revision)
- `DB_PATH` SQLite database location (default `./data/app.db`)
- `MAX_WIDTH` maximum image width
- `MAX_HEIGHT` maximum image height
- `MAX_STEPS` maximum inference steps
- `MAX_UPLOAD_MB` max upload size in MB (default 10)
- `MAX_CONCURRENT_JOBS` maximum concurrent jobs (default `1`)
- `QUALITY_PROFILE` auto|low|balanced|high|ultra|cpu-low|cpu-balanced
- `ENABLED_MODELS` optional comma-separated model ids to load (e.g. `qwen-image-2512` or `flux2-klein-9b-gguf`)
- `DEFAULT_WIDTH` override default width
- `DEFAULT_HEIGHT` override default height
- `DEFAULT_STEPS` override default steps
- `ENABLE_ATTENTION_SLICING` reduce memory usage during attention (default `1`)
- `ENABLE_VAE_SLICING` reduce memory usage during VAE decode (default `1`)
- `ENABLE_VAE_TILING` reduce memory usage for large images (default `0`)
- `WARMUP_MODELS` pre-load pipelines on startup (default `1`)
- `WARMUP_TIMEOUT_SEC` warmup timeout before reporting degraded readiness (default `300`)
- `DEBUG` include prompts in logs (default `0`)
- `SAFETY_REVIEW_MODE` manual|off (default `manual`, required for FLUX.2)
- `FLUX2_MODEL_DIR` local path for FLUX assets (default `./models/flux2_klein_9b_gguf`)
- `FLUX2_DIFFUSION_GGUF` path to GGUF diffusion model
- `FLUX2_VAE` path to `flux2-vae.safetensors`
- `FLUX2_TEXT_ENCODER` path to `qwen_3_8b_fp4mixed.safetensors` (or fp8 mixed if preferred)
- `FLUX2_TEXT_ENCODER_PRECISION` fp4 or fp8 (used if `FLUX2_TEXT_ENCODER` is not set)
- `FLUX2_LLM_GGUF` GGUF LLM path for sd-cli (`--llm`)
- `FLUX2_TEXT_ENCODER_GGUF` legacy GGUF text encoder path (fallback)
- `FLUX2_USE_PY_BINDINGS` enable stable-diffusion-cpp-python (default `1`)
- `FLUX2_USE_SDCLI_FALLBACK` enable sd-cli fallback (default `1`)
- `FLUX2_SDCLI_PATH` sd-cli binary path or name (default `sd`)
- `FLUX2_SDCLI_EXTRA_ARGS` extra args passed to sd-cli
- `FLUX2_DEFAULT_STEPS` default steps for FLUX (default `4`)
- `FLUX2_DEFAULT_GUIDANCE` default guidance for FLUX (default `4.0`)
- `FLUX2_DEFAULT_SIZE` default size for FLUX (default `1024`)
- `FLUX2_DEFAULT_STRENGTH` default edit strength (default `0.65`)
- `SDXL_OV_BASE_DIR` local path to SDXL OpenVINO base IR
- `SDXL_OV_REFINER_DIR` local path to SDXL OpenVINO refiner IR
- `SDXL_OV_DEVICE` OpenVINO device (default `CPU`)
- `SDXL_OV_COMPILE` enable OpenVINO compile step (default `1`)
- `SDXL_REFINER_ENABLED` enable SDXL refiner (default `0`)
- `SDXL_REFINER_DENOISING_START` refiner denoising start (default `0.8`)

Frontend (`frontend/.env.example`):
- `NEXT_PUBLIC_BACKEND_URL` backend base URL (default `http://localhost:8000`)

See `frontend/ENV.md` for full frontend env documentation.

## Notes

- CORS is enabled for `http://localhost:3000` in dev.
- The `/arena` route calls the backend health check and displays the status.
- The `/chat` route is the primary UI for generate/edit jobs (uses SSE + job queue).
- Offline mode sets `HF_HOME`, `HF_HUB_CACHE`, and `TRANSFORMERS_CACHE` under `models/cache`.
- Install dependencies (including diffusers from GitHub) before disabling the network.
- `torchvision` enables faster image preprocessing; `accelerate` reduces CPU memory spikes during load.
  - For lower RAM usage, keep image sizes <= 768 and steps <= 20 on CPU.
- Uploads accept PNG/JPEG/WEBP and enforce `MAX_UPLOAD_MB`.

## Offline checklist

- Mirror models locally (`python scripts/mirror_models.py`).
- Ensure `OFFLINE_MODE=1` so `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1`.
- Start backend only after dependencies are installed (no network calls during inference).

## Warmup + readiness

- `/health` is a liveness check (process up).
- `/ready` is a readiness check (pipelines loaded). If warmup fails or times out, readiness is
  marked degraded but the API stays live.

## Error responses

All API errors return a consistent shape:
```json
{ "error": { "code": "...", "message": "...", "details": {} } }
```

## Job recovery

If the backend restarts, any jobs that were running or queued are marked failed with
`server restarted` so the UI can explicitly replay them.

## Backup & restore

- Backup `data/app.db` (job + run history) and `data/images/` (stored PNGs).
- Restore both together to keep history references intact.
- Auto profile uses hardware detection; remove `MAX_WIDTH/MAX_HEIGHT/MAX_STEPS` from `backend/.env` to let it tune limits.

## Inference quickstart (Step 2)

Example text-to-image request:
```bash
curl -X POST http://localhost:8000/api/infer/t2i \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "qwen-image-2512",
    "prompt": "a cinematic portrait of a robot painter",
    "negative_prompt": "blurry, low quality",
    "seed": 1234,
    "steps": 20,
    "width": 1024,
    "height": 1024,
    "guidance_scale": 4.0,
    "true_cfg_scale": 1.0
  }'
```

The `/api/infer/*` endpoints are synchronous and intended for internal/debug use. The UI should use
the job queue endpoints below.

## Job queue + SSE (Step 3)

Submit a job and stream progress:
```bash
curl -X POST http://localhost:8000/api/jobs/t2i \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "qwen-image-2512",
    "prompt": "a cinematic portrait of a robot painter",
    "negative_prompt": "blurry, low quality",
    "seed": 1234,
    "steps": 20,
    "width": 1024,
    "height": 1024,
    "guidance_scale": 4.0,
    "true_cfg_scale": 1.0
  }'
```

```bash
curl -N http://localhost:8000/api/jobs/<job_id>/events
```

Completed jobs and runs persist in `data/app.db` so the UI can reload history.

## Chat UI (Step 4)

The `/chat` UI submits jobs via the queue endpoints and streams progress over SSE. Editing flows
upload images first (`/api/images/upload`) and then pass the returned `image_id` values into
`/api/jobs/edit`. If you leave the seed blank, the backend generates one and stores it in run
metadata.

## Running tests

Inference tests are heavy (especially on CPU). By default they are skipped unless you opt in:

- Enable all inference tests: `setx RUN_INFERENCE_TESTS 1`
- Allow CPU inference tests: `setx RUN_CPU_INFERENCE_TESTS 1`

Then run: `python -m unittest discover -s backend/tests`
