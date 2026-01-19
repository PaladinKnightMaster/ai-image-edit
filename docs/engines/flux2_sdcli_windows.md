# FLUX.2 klein (sd-cli) on Windows

Use `sd-cli.exe` (stable-diffusion.cpp) for the most stable FLUX.2 klein runtime on Windows.

## 1) Download sd-cli

```powershell
powershell -ExecutionPolicy Bypass -File scripts/fetch_sdcli.ps1 -Variant avx2
```

The script prints the resolved `sd.exe`/`sd-cli.exe` path. Use that in `FLUX2_SDCLI_PATH`.

Variants:
- `avx2` (default, recommended)
- `avx`
- `noavx`
- `cuda12` (NVIDIA GPU build)

## 2) Download FLUX2 assets + LLM GGUF

```powershell
powershell -ExecutionPolicy Bypass -File scripts/fetch_flux2_klein_gguf.ps1
python scripts/verify_flux2_klein_assets.py
```

This downloads:
- diffusion GGUF
- VAE safetensors
- text encoder safetensors (for pybindings)
- Qwen3‑8B GGUF LLM for sd‑cli (`--llm`)

## 3) Configure backend env

`backend/.env`:
```
FLUX2_USE_PY_BINDINGS=0
FLUX2_USE_SDCLI_FALLBACK=1
FLUX2_SDCLI_PATH=tools\sdcli\master-474-61659ef\avx2\sd.exe
FLUX2_LLM_GGUF=./models/flux2_klein_9b_gguf/text_encoder_gguf/Qwen3-8B-Q6_K.gguf
```

## 4) Diagnostics + smoke test

```powershell
python scripts/diagnose_flux2_sdcli.py
```

Manual smoke test (adjust paths):
```powershell
sd.exe --diffusion-model models\flux2_klein_9b_gguf\diffusion_model\flux-2-klein-9b-Q4_K_M.gguf `
  --vae models\flux2_klein_9b_gguf\vae\flux2-vae.safetensors `
  --llm models\flux2_klein_9b_gguf\text_encoder_gguf\Qwen3-8B-Q6_K.gguf `
  -p "A cat holding a sign that says hello world" -W 512 -H 512 --steps 4 --cfg-scale 4 --seed 0 `
  -o output.png
```

For edit/img2img:
```powershell
sd.exe --diffusion-model models\flux2_klein_9b_gguf\diffusion_model\flux-2-klein-9b-Q4_K_M.gguf `
  --vae models\flux2_klein_9b_gguf\vae\flux2-vae.safetensors `
  --llm models\flux2_klein_9b_gguf\text_encoder_gguf\Qwen3-8B-Q6_K.gguf `
  -r input.png -p "Change the background to a park" -W 512 -H 512 --steps 4 --cfg-scale 4 --seed 0 `
  -o output.png
```

## Notes

- sd-cli is more stable than pybindings on Windows for FLUX2.
- If you switch variants, update `FLUX2_SDCLI_PATH` accordingly.
