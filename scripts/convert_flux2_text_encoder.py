from __future__ import annotations

import argparse
import os
from pathlib import Path


def _mb(size: int) -> float:
    return round(size / (1024 * 1024), 1)


def _resolve(path: str | Path, base: Path) -> Path:
    value = Path(path)
    if value.is_absolute():
        return value
    return (base / value).resolve()


def _default_paths(precision: str) -> tuple[Path, Path]:
    repo_root = Path(__file__).resolve().parents[1]
    model_dir = repo_root / "models" / "flux2_klein_9b_gguf" / "text_encoder"
    input_name = f"qwen_3_8b_{precision}mixed.safetensors"
    output_name = f"qwen_3_8b_{precision}mixed.gguf"
    return model_dir / input_name, model_dir / output_name


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert FLUX2 text encoder safetensors to GGUF for stable-diffusion.cpp.",
    )
    parser.add_argument(
        "--precision",
        choices=["fp4", "fp8"],
        default=os.getenv("FLUX2_TEXT_ENCODER_PRECISION", "fp4"),
        help="Text encoder precision (matches downloaded safetensors).",
    )
    parser.add_argument(
        "--input",
        help="Path to safetensors text encoder.",
    )
    parser.add_argument(
        "--output",
        help="Path to write GGUF output.",
    )
    parser.add_argument(
        "--output-type",
        default="q4_k",
        help="GGUF output type (e.g., q4_k, f16).",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    default_input, default_output = _default_paths(args.precision)
    input_path = _resolve(args.input, repo_root) if args.input else default_input
    output_path = _resolve(args.output, repo_root) if args.output else default_output

    if not input_path.exists():
        raise SystemExit(f"Input not found: {input_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        import stable_diffusion_cpp  # type: ignore
    except Exception as exc:
        raise SystemExit(
            "stable-diffusion-cpp-python is required. Install with:\n"
            "  pip install -r backend/requirements-flux.txt"
        ) from exc

    model = stable_diffusion_cpp.StableDiffusion()
    ok = model.convert(
        input_path=str(input_path),
        output_path=str(output_path),
        output_type=args.output_type,
    )
    if not ok:
        raise SystemExit("Conversion failed. Check stable-diffusion.cpp logs.")

    size = output_path.stat().st_size
    if size < 1_000_000_000:
        output_path.unlink(missing_ok=True)
        raise SystemExit(
            f"Converted GGUF is too small ({_mb(size)} MB). Conversion likely failed."
        )

    print(f"Saved {output_path} ({_mb(size)} MB)")
    print("Set FLUX2_TEXT_ENCODER_GGUF to this path before starting the backend.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
