from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = REPO_ROOT / "backend"

sys.path.insert(0, str(BACKEND_DIR))

from app import config, model_registry  # noqa: E402


def main() -> None:
    if os.getenv("HF_HUB_OFFLINE") != "1":
        raise SystemExit("HF_HUB_OFFLINE is not set to 1. Check OFFLINE_MODE in backend config.")
    if os.getenv("TRANSFORMERS_OFFLINE") != "1":
        raise SystemExit(
            "TRANSFORMERS_OFFLINE is not set to 1. Check OFFLINE_MODE in backend config."
        )

    try:
        import diffusers  # noqa: F401
    except ImportError as exc:
        raise SystemExit(
            "diffusers is not installed. Install it before running this smoke test."
        ) from exc

    statuses = model_registry.list_models()
    missing = [entry for entry in statuses if not entry["present"]]
    if missing:
        details = "\n".join(
            f"- {entry['id']}: {entry['local_path']}" for entry in missing
        )
        raise SystemExit(
            "Missing local model files:\n"
            f"{details}\n"
            "Run: python scripts/mirror_models.py"
        )

    print("Offline configuration is active. Models are present on disk.")


if __name__ == "__main__":
    main()
