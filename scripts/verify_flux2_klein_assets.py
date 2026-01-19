from __future__ import annotations

import argparse
import os
from pathlib import Path

MIN_GGUF_BYTES = 1 * 1024 * 1024 * 1024
MIN_VAE_BYTES = 100 * 1024 * 1024
MIN_TEXT_ENCODER_BYTES = 1 * 1024 * 1024 * 1024
MIN_LLM_BYTES = 1 * 1024 * 1024 * 1024


def _root() -> Path:
    return Path(__file__).resolve().parents[1]


def _asset_path(env_name: str, default_rel: str) -> Path:
    value = os.getenv(env_name)
    if value:
        return Path(value).expanduser().resolve()
    return (_root() / default_rel).resolve()


def _format_size(bytes_value: int) -> str:
    mb = bytes_value / (1024 * 1024)
    gb = bytes_value / (1024 * 1024 * 1024)
    return f"{mb:.1f} MB / {gb:.2f} GB"


def _check_size(path: Path, min_bytes: int, label: str) -> str | None:
    if not path.exists():
        return f"{label} missing at {path}"
    size = path.stat().st_size
    if size < min_bytes:
        return f"{label} too small ({_format_size(size)}) at {path}"
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify FLUX.2 klein assets.")
    default_precision = os.getenv("FLUX2_TEXT_ENCODER_PRECISION", "fp4").lower()
    if default_precision not in {"fp4", "fp8"}:
        default_precision = "fp4"
    parser.add_argument(
        "--text-encoder",
        choices=["fp4", "fp8"],
        default=default_precision,
        help="Text encoder precision (fp4 or fp8) when FLUX2_TEXT_ENCODER is not set.",
    )
    args = parser.parse_args()

    text_encoder_name = f"qwen_3_8b_{args.text_encoder}mixed.safetensors"

    diffusion = _asset_path(
        "FLUX2_DIFFUSION_GGUF",
        "models/flux2_klein_9b_gguf/diffusion_model/flux-2-klein-9b-Q4_K_M.gguf",
    )
    vae = _asset_path(
        "FLUX2_VAE",
        "models/flux2_klein_9b_gguf/vae/flux2-vae.safetensors",
    )
    text_encoder = _asset_path(
        "FLUX2_TEXT_ENCODER",
        f"models/flux2_klein_9b_gguf/text_encoder/{text_encoder_name}",
    )
    llm_gguf = _asset_path(
        "FLUX2_LLM_GGUF",
        "models/flux2_klein_9b_gguf/text_encoder_gguf/Qwen3-8B-Q6_K.gguf",
    )
    text_encoder_gguf = os.getenv("FLUX2_TEXT_ENCODER_GGUF")
    legacy_gguf_path = None
    if text_encoder_gguf:
        legacy_gguf_path = Path(text_encoder_gguf).expanduser().resolve()

    errors: list[str] = []
    errors.extend(
        filter(
            None,
            [
                _check_size(diffusion, MIN_GGUF_BYTES, "GGUF diffusion model"),
                _check_size(vae, MIN_VAE_BYTES, "VAE"),
                _check_size(text_encoder, MIN_TEXT_ENCODER_BYTES, "Text encoder"),
                _check_size(llm_gguf, MIN_LLM_BYTES, "LLM GGUF"),
            ],
        )
    )
    if legacy_gguf_path and not legacy_gguf_path.exists():
        errors.append(f"Legacy text encoder GGUF missing at {legacy_gguf_path}")

    if errors:
        print("FLUX.2 klein assets invalid:")
        for error in errors:
            print(f"- {error}")
        print("Run: scripts/fetch_flux2_klein_gguf.ps1 (or .sh) to download.")
        return 1

    print("FLUX.2 klein assets found:")
    print(f"- diffusion: {diffusion} ({_format_size(diffusion.stat().st_size)})")
    print(f"- vae: {vae} ({_format_size(vae.stat().st_size)})")
    print(f"- text encoder: {text_encoder} ({_format_size(text_encoder.stat().st_size)})")
    print(f"- llm gguf: {llm_gguf} ({_format_size(llm_gguf.stat().st_size)})")
    if legacy_gguf_path:
        print(
            f"- legacy text encoder gguf: {legacy_gguf_path} "
            f"({_format_size(legacy_gguf_path.stat().st_size)})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
