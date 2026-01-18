# AI Image Edit (V1)

Offline-first, self-hosted AI image generator/editor with an LMArena-style UI. This step delivers a
clean monorepo skeleton with a Next.js frontend and FastAPI backend, plus a hello-world health check
between them.

## Repo layout

- `frontend/` Next.js App Router + Tailwind UI
- `backend/` FastAPI service
- `scripts/` model mirroring + smoke utilities
- `data/` local persistence (empty)
- `models/` local model assets + caches

## Quickstart

Backend:
1) `python -m venv .venv`
2) Activate the venv
   - Windows PowerShell: `./.venv/Scripts/Activate.ps1`
   - macOS/Linux: `source .venv/bin/activate`
3) `pip install -r backend/requirements.txt` (CPU, requires `git` on PATH)
   - GPU: `pip install -r backend/requirements-gpu.txt` (edit CUDA version if needed)
4) Copy env vars: `copy backend/.env.example backend/.env`
5) Run: `make dev-backend`

Frontend:
1) `cd frontend`
2) `npm install`
3) Copy env vars: `copy .env.example .env.local`
4) Run: `make dev-frontend`
5) Open `http://localhost:3000/chat`

Run both:
- `make dev`

If you do not have GNU Make installed, run these directly:
- Backend: `cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- Frontend: `cd frontend && npm run dev`

## Offline model mirroring

Mirror the required Qwen models to local disk so the backend can run with the network disabled.

1) `python scripts/mirror_models.py`
2) Optional revision pinning: `python scripts/mirror_models.py --revision main`

This writes to `models/hf/<org>/<name>/<revision>/...` and the backend reads from `MODEL_ROOT`.

Smoke-check offline config + model presence (requires `diffusers` installed):
- `python scripts/smoke_offline_load.py`

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
- `POST /api/jobs/replay` -> `{ "job_id": "..." }`
- `GET /api/jobs/{job_id}` -> job + run metadata
- `GET /api/jobs/{job_id}/events` -> SSE stream
- `GET /api/runs` -> recent runs (supports `status=failed`)
- `GET /api/runs/{run_id}/export` -> reproducibility export JSON
- `GET /api/stats` -> queue + latency summary

## Environment variables

Backend (`backend/.env.example`):
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
- `DEFAULT_WIDTH` override default width
- `DEFAULT_HEIGHT` override default height
- `DEFAULT_STEPS` override default steps
- `ENABLE_ATTENTION_SLICING` reduce memory usage during attention (default `1`)
- `ENABLE_VAE_SLICING` reduce memory usage during VAE decode (default `1`)
- `ENABLE_VAE_TILING` reduce memory usage for large images (default `0`)
- `WARMUP_MODELS` pre-load pipelines on startup (default `1`)
- `WARMUP_TIMEOUT_SEC` warmup timeout before reporting degraded readiness (default `300`)
- `DEBUG` include prompts in logs (default `0`)

Frontend (`frontend/.env.example`):
- `NEXT_PUBLIC_BACKEND_URL` backend base URL (default `http://localhost:8000`)

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
