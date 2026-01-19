from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path


MIN_GGUF_BYTES = 1 * 1024 * 1024 * 1024
MIN_VAE_BYTES = 100 * 1024 * 1024
MIN_TEXT_ENCODER_BYTES = 1 * 1024 * 1024 * 1024
MIN_LLM_BYTES = 1 * 1024 * 1024 * 1024

GGUF_REPO = "unsloth/FLUX.2-klein-9B-GGUF"
COMFY_REPO = "Comfy-Org/flux2-klein-9B"
LLM_REPO = "Qwen/Qwen3-8B-GGUF"
VAE_PATH = "split_files/vae/flux2-vae.safetensors"
DEFAULT_LLM_FILE = "Qwen3-8B-Q6_K.gguf"


def _root() -> Path:
    return Path(__file__).resolve().parents[1]


def _parse_args() -> argparse.Namespace:
    default_precision = os.getenv("FLUX2_TEXT_ENCODER_PRECISION", "fp4").lower()
    if default_precision not in {"fp4", "fp8"}:
        default_precision = "fp4"
    parser = argparse.ArgumentParser(description="Download FLUX.2 klein assets.")
    parser.add_argument(
        "--output-dir",
        default=str(_root() / "models" / "flux2_klein_9b_gguf"),
        help="Base output directory for model assets.",
    )
    parser.add_argument(
        "--quant",
        default="Q4_K_M",
        help="GGUF quant to download (default: Q4_K_M).",
    )
    parser.add_argument(
        "--text-encoder",
        choices=["fp4", "fp8"],
        default=default_precision,
        help="Text encoder precision (fp4 or fp8).",
    )
    parser.add_argument(
        "--llm-file",
        default=DEFAULT_LLM_FILE,
        help="GGUF LLM filename to download (default: Qwen3-8B-Q6_K.gguf).",
    )
    parser.add_argument(
        "--skip-llm",
        action="store_true",
        help="Skip downloading the GGUF LLM file.",
    )
    parser.add_argument(
        "--token",
        default=None,
        help="HF token (optional, otherwise uses HF_TOKEN env).",
    )
    parser.add_argument(
        "--clean-cache",
        action="store_true",
        help="Clear helper download cache before downloading.",
    )
    return parser.parse_args()


def _require_hf() -> tuple[object, str]:
    try:
        import huggingface_hub  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "huggingface_hub is required. Install with: pip install 'huggingface_hub>=0.32.0'"
        ) from exc

    version = getattr(huggingface_hub, "__version__", "0.0.0")
    parts = version.split(".")
    try:
        parsed = tuple(int(p) for p in parts[:3])
    except ValueError:
        parsed = (0, 0, 0)
    if parsed < (0, 32, 0):
        raise RuntimeError(
            f"huggingface_hub>=0.32.0 is required (found {version}). "
            "Run: pip install 'huggingface_hub>=0.32.0'"
        )
    return huggingface_hub, version


def _format_size(bytes_value: int) -> str:
    mb = bytes_value / (1024 * 1024)
    gb = bytes_value / (1024 * 1024 * 1024)
    return f"{mb:.1f} MB / {gb:.2f} GB"


def _validate_size(path: Path, min_bytes: int, label: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"{label} not found at {path}")
    size = path.stat().st_size
    if size < min_bytes:
        path.unlink(missing_ok=True)
        raise RuntimeError(
            f"{label} is too small ({_format_size(size)}). "
            "The download likely returned an error page. Deleted the file."
        )


def _download_file(
    hub,
    repo_id: str,
    file_path: str,
    dest_path: Path,
    token: str | None,
    min_bytes: int,
    cache_dir: Path,
) -> None:
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    if dest_path.exists():
        size = dest_path.stat().st_size
        if size >= min_bytes:
            print(f"Skip (exists): {dest_path} ({_format_size(size)})")
            return
        dest_path.unlink(missing_ok=True)

    print(f"Downloading {repo_id}:{file_path} -> {dest_path}")
    try:
        hub.snapshot_download(
            repo_id=repo_id,
            allow_patterns=[file_path],
            local_dir=cache_dir,
            token=token,
        )
    except Exception as exc:  # pragma: no cover
        message = str(exc)
        if "xet" in message.lower():
            message += "\nInstall hf-xet if the repo uses Xet: pip install hf-xet"
        raise RuntimeError(f"Download failed for {repo_id}:{file_path}. {message}") from exc

    source_path = cache_dir / file_path
    if not source_path.exists():
        raise RuntimeError(f"Downloaded file not found at {source_path}")

    shutil.copy2(source_path, dest_path)
    _validate_size(dest_path, min_bytes, dest_path.name)
    print(f"Saved {dest_path} ({_format_size(dest_path.stat().st_size)})")


def main() -> int:
    args = _parse_args()
    try:
        hub, _version = _require_hf()
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1

    output_dir = Path(args.output_dir).expanduser().resolve()
    cache_dir = output_dir / ".downloads"
    if args.clean_cache and cache_dir.exists():
        shutil.rmtree(cache_dir, ignore_errors=True)

    token = args.token or os.getenv("HF_TOKEN")
    quant = args.quant
    text_encoder_precision = args.text_encoder
    llm_file = args.llm_file

    gguf_name = f"flux-2-klein-9b-{quant}.gguf"
    gguf_dest = output_dir / "diffusion_model" / gguf_name
    vae_dest = output_dir / "vae" / "flux2-vae.safetensors"
    text_encoder_name = f"qwen_3_8b_{text_encoder_precision}mixed.safetensors"
    text_encoder_dest = output_dir / "text_encoder" / text_encoder_name
    llm_dest = output_dir / "text_encoder_gguf" / llm_file

    try:
        _download_file(
            hub,
            GGUF_REPO,
            gguf_name,
            gguf_dest,
            token=token,
            min_bytes=MIN_GGUF_BYTES,
            cache_dir=cache_dir / "gguf",
        )
        _download_file(
            hub,
            COMFY_REPO,
            VAE_PATH,
            vae_dest,
            token=token,
            min_bytes=MIN_VAE_BYTES,
            cache_dir=cache_dir / "comfy",
        )
        _download_file(
            hub,
            COMFY_REPO,
            f"split_files/text_encoders/{text_encoder_name}",
            text_encoder_dest,
            token=token,
            min_bytes=MIN_TEXT_ENCODER_BYTES,
            cache_dir=cache_dir / "comfy",
        )
        if not args.skip_llm:
            _download_file(
                hub,
                LLM_REPO,
                llm_file,
                llm_dest,
                token=token,
                min_bytes=MIN_LLM_BYTES,
                cache_dir=cache_dir / "llm",
            )
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1

    print("FLUX.2 klein assets ready under:", output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
