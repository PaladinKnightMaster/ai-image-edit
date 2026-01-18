from __future__ import annotations

import argparse
import os
from pathlib import Path

from huggingface_hub import snapshot_download

MODELS = (
    ("qwen-image-2512", "Qwen/Qwen-Image-2512"),
    ("qwen-image-edit-2511", "Qwen/Qwen-Image-Edit-2511"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mirror Hugging Face models locally.")
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Root directory for model snapshots (default: ./models/hf).",
    )
    parser.add_argument(
        "--revision",
        default=None,
        help="Optional revision to mirror (applies to both models).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    output_root = Path(args.output_dir) if args.output_dir else repo_root / "models" / "hf"
    revision = args.revision
    revision_dir = revision or "main"

    os.environ["HF_HUB_OFFLINE"] = "0"
    os.environ["TRANSFORMERS_OFFLINE"] = "0"
    os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")

    output_root.mkdir(parents=True, exist_ok=True)

    for model_id, repo_id in MODELS:
        org, name = repo_id.split("/", 1)
        local_dir = output_root / org / name / revision_dir
        local_dir.mkdir(parents=True, exist_ok=True)
        resolved_path = snapshot_download(
            repo_id=repo_id,
            revision=revision,
            local_dir=str(local_dir),
            local_dir_use_symlinks=False,
        )
        print(f"{model_id}: {resolved_path}")


if __name__ == "__main__":
    main()
