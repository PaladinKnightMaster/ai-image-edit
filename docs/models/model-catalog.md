# Model Catalog

This document separates three concepts that were previously mixed together:

1. mirrored model assets
2. registered runtime runners
3. MVP-supported product lanes

## Current runner catalog

| Model id | Capability | Runtime | Current status | MVP role |
| --- | --- | --- | --- | --- |
| `qwen-image-2512` | T2I | Diffusers | implemented | supporting lane |
| `qwen-image-edit-2511` | edit | Diffusers | implemented | primary edit lane |
| `flux2-klein-9b-gguf` | T2I + edit | stable-diffusion.cpp | implemented | optional advanced lane |
| `sdxl-openvino` | T2I | OpenVINO | implemented, edit not supported | research lane |

## Current mirrored assets

The mirror script covers the Qwen family and preflights the machine before downloading:

- `scripts/mirror_models.py`
  - `qwen-image-2512`
  - `qwen-image-edit-2511`

FLUX and SDXL OpenVINO use separate provisioning paths and env-driven asset locations.

## Download, hardware fit, and removal

- Full command blocks and per-model requirements: `docs/models/download-and-setup.md`
- Hardware scan + recommendation (Ollama-style): `python scripts/scan_machine.py`,
  or `GET /api/hardware` from the running backend (source: `backend/app/hardware.py`)
- Safe removal to reclaim disk: `python scripts/remove_model.py --model <id>`

Nothing is auto-downloaded. Qwen (~45 GB, ~20B params) is treated as GPU-only / off-box:
the mirror script refuses to pull it onto an unsuitable machine unless `--force` is given.

## Lane definitions

### `qwen-image-2512`

- role: secondary generation lane
- capability: text-to-image
- loader: `DiffusionPipeline.from_pretrained(...)`
- asset source: mirrored local Hugging Face snapshot

### `qwen-image-edit-2511`

- role: primary edit lane
- capability: prompt-guided image editing with one or two input images
- loader: `QwenImageEditPlusPipeline.from_pretrained(...)`
- asset source: mirrored local Hugging Face snapshot

### `flux2-klein-9b-gguf`

- role: optional advanced lane
- capability: text-to-image and image-to-image edit
- loaders:
  - pybindings
  - `sd-cli` fallback
- asset source: GGUF and associated local files
- note: manual review gate is expected

### `sdxl-openvino`

- role: CPU acceleration research lane
- capability: text-to-image only
- loader: Optimum Intel OpenVINO pipelines
- note: optional refiner exists, but edit is not implemented

## Product policy

- MVP core:
  - `qwen-image-edit-2511`
  - `qwen-image-2512`
- optional advanced lane:
  - `flux2-klein-9b-gguf`
- research lane:
  - `sdxl-openvino`

## Documentation rule

Future docs should state separately:

- whether a lane is registered
- whether a lane is mirrored automatically
- whether a lane is MVP-supported
- whether a lane is research-only
