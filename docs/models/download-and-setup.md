# Model Download & Setup Guide

This guide explains how to pick, download, and remove image models for AI Image Edit.
Models are **not** bundled or auto-downloaded. Some (the Qwen family, ~45 GB each) only
run well on a CUDA GPU, so the tooling refuses to pull them onto an unsuitable machine
unless you explicitly override.

Related:
- Runner catalog and MVP roles: `docs/models/model-catalog.md`
- Env vars for asset paths: `README.md` (Environment variables) and `backend/ENV.md`

## 1. Scan your machine first

Let the advisor tell you what fits, Ollama-style:

```bash
python scripts/scan_machine.py
```

It prints your CPU/RAM/GPU/disk and a best-first list of models with a verdict for each
(`Recommended`, `Usable (slow)`, `Needs more RAM/disk`, `Needs a GPU (off-box)`), plus the
exact setup command for the best pick. JSON for tooling/UI:

```bash
python scripts/scan_machine.py --json
```

The running backend exposes the same data at `GET /api/hardware`. The `/chat`
sidebar **Hardware fit** panel shows the live recommendation and can switch the
active model to the best local pick.

## 2. Model matrix

| Model id | Capability | Engine | Approx disk | Runs on CPU? | Best on |
| --- | --- | --- | --- | --- | --- |
| `sdxl-openvino` | t2i + edit | OpenVINO | ~7 GB | Yes (fast) | Intel CPU/iGPU |
| `flux2-klein-9b-gguf` | t2i + edit | stable-diffusion.cpp | ~12 GB | Yes (very slow) | GPU (Vulkan/CUDA) |
| `qwen-image-2512` | t2i | diffusers | ~45 GB | No | CUDA GPU >=24 GB |
| `qwen-image-edit-2511` | edit | diffusers | ~45 GB | No | CUDA GPU >=24 GB |

Rule of thumb: on a **CPU-only Intel machine**, use `sdxl-openvino` for both generation
and prompt-guided edit; treat the Qwen family as GPU-only / off-box.

## 3. Download

### sdxl-openvino

Best local pick for Intel CPUs/iGPUs. Supports **text-to-image and img2img edit** from
one OpenVINO export (edit is lazy-loaded from the same base directory).

**Preferred path (pre-converted INT8, ~3.3 GB, no local quantization):**

```bash
pip install -r backend/requirements-openvino.txt
hf download OpenVINO/stable-diffusion-xl-base-1.0-int8-ov \
  --local-dir models/openvino/sdxl_base \
  --exclude "*.ipynb_checkpoints*"

# backend/.env
# SDXL_OV_BASE_DIR=./models/openvino/sdxl_base
# ENABLED_MODELS=sdxl-openvino
```

**Alternative (local export from a PyTorch checkpoint):**

```bash
pip install -r backend/requirements-openvino.txt
optimum-cli export openvino \
  --model stabilityai/stable-diffusion-xl-base-1.0 \
  --variant fp16 \
  --weight-format int8 \
  models/openvino/sdxl_base
```

Tip: for seconds-per-image on CPU, use a few-step checkpoint (SDXL-Turbo / LCM /
SDXL-Lightning) instead of the 30-step base, and lower `DEFAULT_STEPS`.
Edit uses prompt-guided img2img with default strength `0.65` (overridable per job).

### flux2-klein-9b-gguf

Optional advanced lane. Runs on CPU but is very slow (~30-40 min/image); much faster with
a GPU. Full details (quant options, sd-cli fallback, Windows notes) are in `README.md`
under "FLUX.2 klein GGUF".

```bash
# Linux/macOS
bash scripts/fetch_flux2_klein_gguf.sh
python scripts/verify_flux2_klein_assets.py

# Windows (PowerShell)
powershell -ExecutionPolicy Bypass -File scripts/fetch_flux2_klein_gguf.ps1
python scripts/verify_flux2_klein_assets.py
```

### Qwen-Image family

Frontier quality, but ~20B parameters. The current diffusers runtime loads fp32 on CPU,
so these are **GPU-only / off-box** in practice. The mirror script preflights your machine
and refuses to download them on a CPU-only box unless you pass `--force`.

```bash
# See what fits before downloading
python scripts/mirror_models.py --list

# Download a specific model (asks for confirmation)
python scripts/mirror_models.py --model qwen-image-2512
python scripts/mirror_models.py --model qwen-image-edit-2511 --yes

# Both Qwen models
python scripts/mirror_models.py --all

# On a machine the preflight flags as unsuitable (e.g. no GPU), override intentionally:
python scripts/mirror_models.py --model qwen-image-edit-2511 --force --yes
```

After download, enable the lane and (optionally) run it off-box on GPU hardware:

```bash
# backend/.env
# ENABLED_MODELS=qwen-image-edit-2511
```

## 4. Remove models to reclaim disk

Large weights can be deleted safely; removal only ever touches paths inside `models/`.

```bash
# List known model ids
python scripts/remove_model.py --list

# Preview what would be deleted (size, paths) without deleting
python scripts/remove_model.py --model qwen-image-2512 --dry-run

# Delete (asks for confirmation unless --yes)
python scripts/remove_model.py --model qwen-image-edit-2511 --yes
```

`/api/models` and `scan_machine.py` will show the lane as not present again after removal.

## 5. Quick start for a CPU-only Intel machine

```bash
python scripts/scan_machine.py                                  # -> best pick: sdxl-openvino
pip install -r backend/requirements-openvino.txt
hf download OpenVINO/stable-diffusion-xl-base-1.0-int8-ov \
  --local-dir models/openvino/sdxl_base \
  --exclude "*.ipynb_checkpoints*"
# set SDXL_OV_BASE_DIR + ENABLED_MODELS=sdxl-openvino in backend/.env, then start the backend
```
