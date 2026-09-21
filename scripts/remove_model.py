#!/usr/bin/env python3
"""Safely remove local model assets to reclaim disk space.

Large models (e.g. the ~45 GB Qwen family) can be removed after use. This only ever
deletes inside the repo's `models/` directory and asks for confirmation first.

    python scripts/remove_model.py --list
    python scripts/remove_model.py --model qwen-image-2512 --dry-run
    python scripts/remove_model.py --model qwen-image-edit-2511 --yes
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app import config  # noqa: E402


def _targets_for(model_id: str) -> list[Path]:
    """Local directories that hold a model's assets."""
    from app import model_registry

    spec = model_registry.MODEL_MAP.get(model_id)
    if spec:
        org, name = spec.repo_id.split("/", 1)
        return [config.MODEL_ROOT / org / name]
    if model_id == "flux2-klein-9b-gguf":
        return [config.FLUX2_MODEL_DIR]
    if model_id == "sdxl-openvino":
        return [config.SDXL_OV_BASE_DIR, config.SDXL_OV_REFINER_DIR]
    return []


def _known_ids() -> list[str]:
    from app import model_registry

    return sorted(list(model_registry.MODEL_MAP) + ["flux2-klein-9b-gguf", "sdxl-openvino"])


def _dir_size_gb(path: Path) -> float:
    total = 0
    for child in path.rglob("*"):
        try:
            if child.is_file():
                total += child.stat().st_size
        except OSError:
            continue
    return round(total / (1024**3), 2)


def _is_within_models(path: Path) -> bool:
    models_root = (REPO_ROOT / "models").resolve()
    try:
        path.resolve().relative_to(models_root)
        return True
    except ValueError:
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Remove local model assets safely.")
    parser.add_argument("--model", choices=_known_ids(), help="Model id to remove.")
    parser.add_argument("--list", action="store_true", help="List known model ids and exit.")
    parser.add_argument("--yes", action="store_true", help="Skip the confirmation prompt.")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be removed.")
    args = parser.parse_args()

    if args.list or not args.model:
        print("Known model ids:")
        for model_id in _known_ids():
            print(f"  - {model_id}")
        if not args.model:
            print("\nSpecify one with --model <id>.")
        return

    targets = [p for p in _targets_for(args.model) if p.exists()]
    if not targets:
        print(f"Nothing to remove for '{args.model}' (no local assets found).")
        return

    print(f"Local assets for '{args.model}':")
    total = 0.0
    for path in targets:
        if not _is_within_models(path):
            print(f"  ! refusing to touch path outside models/: {path}")
            sys.exit(2)
        size = _dir_size_gb(path)
        total += size
        print(f"  - {path}  (~{size} GB)")
    print(f"Total: ~{total} GB")

    if args.dry_run:
        print("\n--dry-run: nothing was deleted.")
        return

    if not args.yes:
        try:
            answer = input(f"Delete these assets for '{args.model}'? [y/N] ").strip().lower()
        except EOFError:
            answer = ""
        if answer not in {"y", "yes"}:
            print("Aborted.")
            sys.exit(1)

    for path in targets:
        shutil.rmtree(path, ignore_errors=True)
        print(f"Removed {path}")
    print("Done.")


if __name__ == "__main__":
    main()
