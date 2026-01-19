# Backend Environment Variables

This file explains what each backend environment variable does and how to tune it.
Values are read from `backend/.env` on startup; restart the backend after changes.

## Where to set values

- Backend: `backend/.env` (copy from `backend/.env.example`)
- Frontend: `frontend/.env.local` (copy from `frontend/.env.example`)

Paths are interpreted relative to the repo root unless absolute.

The backend auto-loads `backend/.env` on startup via python-dotenv. You can override
the path by setting `DOTENV_PATH`.

## Core settings

- `APP_NAME` name shown in API metadata.
- `APP_VERSION` version label returned by `/api/version`.
- `APP_COMMIT` commit hash/label (defaults to `dev`).
- `FRONTEND_ORIGIN` CORS origin for the UI (default `http://localhost:3000`).
- `DEBUG` set `1` to log full prompts in structured logs.
- `OFFLINE_MODE` set `1` to force offline mode (sets HF offline env vars).
- `DOTENV_PATH` optional override path for the env file.

## Model paths

- `MODEL_ROOT` root for mirrored Qwen models (`models/hf` by default).
- `MODEL_REVISION` optional revision name under each model folder.
- `FLUX2_MODEL_DIR` root folder for FLUX assets.
- `FLUX2_DIFFUSION_GGUF` path to GGUF diffusion weights.
- `FLUX2_VAE` path to VAE safetensors.
- `FLUX2_TEXT_ENCODER` path to text encoder safetensors.
- `FLUX2_LLM_GGUF` path to GGUF LLM for sd-cli (`--llm`).
- `FLUX2_TEXT_ENCODER_PRECISION` `fp4` or `fp8` (used if `FLUX2_TEXT_ENCODER` is unset).
- `FLUX2_TEXT_ENCODER_GGUF` legacy GGUF text encoder path (fallback for sd-cli/pybindings).

## Limits and defaults

- `MAX_WIDTH`, `MAX_HEIGHT` hard cap on output resolution.
- `MAX_STEPS` hard cap on inference steps.
- `MAX_UPLOAD_MB` upload limit for `POST /api/images/upload`.
- `DEFAULT_WIDTH`, `DEFAULT_HEIGHT`, `DEFAULT_STEPS` override defaults.
- `MAX_CONCURRENT_JOBS` default `1` to avoid GPU/CPU contention.

## Quality profile (auto tuning)

- `QUALITY_PROFILE` selects presets: `auto`, `low`, `balanced`, `high`, `ultra`,
  `cpu-low`, `cpu-balanced`.
- In `auto` mode, the backend chooses defaults based on RAM/VRAM.

## Memory tuning

- `ENABLE_ATTENTION_SLICING` reduce attention memory usage.
- `ENABLE_VAE_SLICING` reduce VAE memory usage.
- `ENABLE_VAE_TILING` enable VAE tiling for large images.

## Warmup and readiness

- `WARMUP_MODELS` set `0` to disable warmup (useful on low RAM).
- `WARMUP_TIMEOUT_SEC` timeout for warmup before readiness is marked degraded.

## Model allow-list (load only what you need)

- `ENABLED_MODELS` comma-separated model ids to register and warm.
  Example: `ENABLED_MODELS=qwen-image-2512` or `ENABLED_MODELS=flux2-klein-9b-gguf`.

Supported model ids:
- `qwen-image-2512`
- `qwen-image-edit-2511`
- `flux2-klein-9b-gguf`

## Safety gate

- `SAFETY_REVIEW_MODE` `manual` or `off`.
  - `manual` returns `pending_review` for FLUX jobs until `/api/jobs/{job_id}/reveal`.
  - `off` returns images immediately (not recommended).

## FLUX backend behavior

- `FLUX2_USE_PY_BINDINGS` use stable-diffusion-cpp-python if installed.
- `FLUX2_USE_SDCLI_FALLBACK` allow sd-cli fallback if bindings missing.
- `FLUX2_SDCLI_PATH` path to `sd` binary (sd-cli).
- `FLUX2_SDCLI_EXTRA_ARGS` extra args appended to sd-cli.
- `FLUX2_DEFAULT_STEPS`, `FLUX2_DEFAULT_GUIDANCE`, `FLUX2_DEFAULT_SIZE`
- `FLUX2_DEFAULT_STRENGTH` default strength for img2img edits.
- `FLUX2_PREDICTION` prediction override (default `flux2_flow`).
- `FLUX2_RNG_TYPE` RNG type for CPU (`cpu` recommended on non-CUDA builds).
- `FLUX2_SAMPLER_RNG_TYPE` sampler RNG type (match `FLUX2_RNG_TYPE`).
- `FLUX2_ALLOW_SAFETENSORS_LLM` allow safetensors LLM for pybindings (default: off on Windows).

Windows default:
- If `FLUX2_USE_PY_BINDINGS` is unset, the backend defaults to `0` on Windows
  to avoid access-violation crashes in stable-diffusion.cpp.

## HF cache overrides (optional)

These are optional and rarely needed; defaults point to `models/cache`.

- `HF_CACHE_ROOT`
- `HF_HOME`
- `HF_HUB_CACHE`
- `TRANSFORMERS_CACHE`

## Frontend env

- `NEXT_PUBLIC_BACKEND_URL` backend base URL (default `http://localhost:8000`).

## Common recipes

Low-RAM CPU (single model, no warmup):
```
QUALITY_PROFILE=cpu-low
ENABLED_MODELS=qwen-image-2512
WARMUP_MODELS=0
MAX_WIDTH=640
MAX_HEIGHT=640
MAX_STEPS=20
```

Only FLUX (manual review on):
```
ENABLED_MODELS=flux2-klein-9b-gguf
SAFETY_REVIEW_MODE=manual
```

Offline strict:
```
OFFLINE_MODE=1
```
