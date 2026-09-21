#!/usr/bin/env python3
"""Mirror image models locally, with a hardware/disk safety preflight.

By default this script does NOT download anything: it scans the machine and prints
which models are recommended, so large weights (e.g. ~45 GB Qwen) are never pulled
onto a machine that cannot run them. Download a specific model explicitly:

    python scripts/mirror_models.py --list                 # show recommendations
    python scripts/mirror_models.py --model qwen-image-2512
    python scripts/mirror_models.py --model qwen-image-edit-2511 --yes
    python scripts/mirror_models.py --all                  # both Qwen models

Use --force to override a "needs GPU / needs more RAM/disk" preflight warning.
Only the diffusers/Hugging Face lanes (Qwen family) are handled here; FLUX GGUF and
SDXL OpenVINO use their own provisioning paths (see docs/models/download-and-setup.md).
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

# Diffusers/HF lanes that this script can mirror.
MIRRORABLE = {
    "qwen-image-2512": "Qwen/Qwen-Image-2512",
    "qwen-image-edit-2511": "Qwen/Qwen-Image-Edit-2511",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mirror Hugging Face image models locally.")
    parser.add_argument(
        "--model",
        action="append",
        default=[],
        choices=sorted(MIRRORABLE),
        help="Model id to mirror (repeatable).",
    )
    parser.add_argument("--all", action="store_true", help="Mirror all Qwen models.")
    parser.add_argument("--list", action="store_true", help="Show recommendations and exit.")
    parser.add_argument("--output-dir", default=None, help="Root dir (default: ./models/hf).")
    parser.add_argument("--revision", default=None, help="Optional revision to mirror.")
    parser.add_argument("--yes", action="store_true", help="Skip the confirmation prompt.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Download even if the machine preflight says it is not suitable.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Preflight only; do not download.")
    return parser.parse_args()


def _verdict_for(model_id: str) -> tuple[str, str]:
    from app import hardware

    req = hardware.REQ_BY_ID.get(model_id)
    if not req:
        return "unknown", "No hardware profile for this model."
    return hardware.evaluate_model(req, hardware.detect_hardware())


def _print_recommendations() -> None:
    from app import hardware

    result = hardware.recommend()
    print(result["summary"])
    print()
    for m in result["models"]:
        if m["id"] in MIRRORABLE:
            print(f"- {m['label']}: {m['verdict_label']} — {m['reason']}")
    print("\nRun `python scripts/scan_machine.py` for the full machine report.")


def _confirm(prompt: str, assume_yes: bool) -> bool:
    if assume_yes:
        return True
    try:
        answer = input(f"{prompt} [y/N] ").strip().lower()
    except EOFError:
        return False
    return answer in {"y", "yes"}


def _download(model_ids: list[str], output_root: Path, revision: str | None) -> None:
    from huggingface_hub import snapshot_download

    os.environ["HF_HUB_OFFLINE"] = "0"
    os.environ["TRANSFORMERS_OFFLINE"] = "0"
    os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
    revision_dir = revision or "main"
    output_root.mkdir(parents=True, exist_ok=True)

    for model_id in model_ids:
        repo_id = MIRRORABLE[model_id]
        org, name = repo_id.split("/", 1)
        local_dir = output_root / org / name / revision_dir
        local_dir.mkdir(parents=True, exist_ok=True)
        print(f"Downloading {model_id} ({repo_id}) -> {local_dir}")
        resolved = snapshot_download(
            repo_id=repo_id,
            revision=revision,
            local_dir=str(local_dir),
            local_dir_use_symlinks=False,
        )
        print(f"{model_id}: {resolved}")


def main() -> None:
    args = parse_args()

    if args.list:
        _print_recommendations()
        return

    model_ids = list(dict.fromkeys(args.model))
    if args.all:
        model_ids = list(MIRRORABLE)

    if not model_ids:
        print("Nothing to download. Choose a model explicitly, e.g.:")
        print("    python scripts/mirror_models.py --model qwen-image-2512")
        print("Or see what fits this machine:")
        print("    python scripts/mirror_models.py --list\n")
        _print_recommendations()
        return

    output_root = Path(args.output_dir) if args.output_dir else REPO_ROOT / "models" / "hf"

    blocked = []
    for model_id in model_ids:
        verdict, reason = _verdict_for(model_id)
        tag = {"recommended": "OK", "usable": "OK", "usable_slow": "SLOW"}.get(verdict, "WARN")
        print(f"[{tag}] {model_id}: {reason}")
        if verdict in {"needs_gpu", "needs_more_ram", "needs_more_disk"}:
            blocked.append((model_id, verdict, reason))

    if blocked and not args.force:
        print("\nOne or more models are not suitable for this machine:")
        for model_id, verdict, reason in blocked:
            print(f"  - {model_id}: {reason}")
        print(
            "\nThese downloads are large. If you know what you are doing (e.g. this is a\n"
            "capable GPU box or you plan to run them elsewhere), re-run with --force.\n"
            "See docs/models/download-and-setup.md for GPU/off-box guidance."
        )
        sys.exit(2)

    if args.dry_run:
        print("\n--dry-run: preflight only, no download performed.")
        return

    total_gb = 0.0
    from app import hardware

    for model_id in model_ids:
        req = hardware.REQ_BY_ID.get(model_id)
        if req:
            total_gb += req.approx_disk_gb
    if not _confirm(
        f"\nDownload {len(model_ids)} model(s), ~{total_gb:.0f} GB total. Continue?", args.yes
    ):
        print("Aborted.")
        sys.exit(1)

    _download(model_ids, output_root, args.revision)


if __name__ == "__main__":
    main()
