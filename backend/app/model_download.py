"""In-app download for the recommended local model only.

FLUX and Qwen stay on their existing setup docs. This module refuses any model
the hardware advisor says should not be downloaded, and any model without an
in-app recipe.
"""

from __future__ import annotations

import threading
from pathlib import Path
from typing import Any, Callable

from app import hardware as hardware_advisor
from app import model_location

SDXL_OPENVINO_REPO = "OpenVINO/stable-diffusion-xl-base-1.0-int8-ov"

# model id -> how to fetch it
IN_APP_DOWNLOADS: dict[str, dict[str, Any]] = {
    "sdxl-openvino": {
        "repo_id": SDXL_OPENVINO_REPO,
        "local_dir": lambda: model_location.apply_effective_dir(),
    }
}

ProgressFn = Callable[[int, int | None], None]
Fetcher = Callable[[str, Path, ProgressFn], None]

_lock = threading.Lock()
_state: dict[str, Any] = {
    "model_id": None,
    "status": "idle",
    "bytes_downloaded": 0,
    "bytes_total": None,
    "message": "",
    "error": None,
}


def in_app_model_ids() -> set[str]:
    return set(IN_APP_DOWNLOADS)


def status() -> dict[str, Any]:
    with _lock:
        return dict(_state)


def _set(**updates: Any) -> None:
    with _lock:
        _state.update(updates)


def _default_fetcher(repo_id: str, local_dir: Path, on_progress: ProgressFn) -> None:
    from huggingface_hub import snapshot_download
    from tqdm.auto import tqdm as tqdm_base

    class _Progress(tqdm_base):
        def update(self, n: int | float | None = 1) -> bool | None:
            result = super().update(n)
            total = int(self.total) if self.total else None
            on_progress(int(self.n or 0), total)
            return result

    local_dir.mkdir(parents=True, exist_ok=True)
    snapshot_download(
        repo_id=repo_id,
        local_dir=str(local_dir),
        ignore_patterns=["*.ipynb_checkpoints*"],
        tqdm_class=_Progress,
    )


def start_download(
    model_id: str,
    *,
    advice: dict[str, Any] | None = None,
    fetcher: Fetcher | None = None,
    background: bool = True,
) -> dict[str, Any]:
    """Start a download. Raises ValueError when the model must not be fetched."""
    recipe = IN_APP_DOWNLOADS.get(model_id)
    if recipe is None:
        raise ValueError(
            "This model is not downloaded from the app. Use the setup guide for other models."
        )

    payload = advice if advice is not None else hardware_advisor.recommend()
    match = next((item for item in payload["models"] if item["id"] == model_id), None)
    if match is None:
        raise ValueError(f"Unknown model '{model_id}'.")
    if match.get("present"):
        _set(
            model_id=model_id,
            status="succeeded",
            bytes_downloaded=0,
            bytes_total=None,
            message="Already on disk.",
            error=None,
        )
        return status()
    if not match.get("downloadable"):
        raise ValueError(match.get("reason") or "This model should not be downloaded on this machine.")

    location = model_location.describe()
    if not location["confirmed"]:
        raise ValueError("Confirm the model folder before downloading.")

    with _lock:
        if _state["status"] == "running":
            return dict(_state)
        _state.update(
            {
                "model_id": model_id,
                "status": "running",
                "bytes_downloaded": 0,
                "bytes_total": None,
                "message": f"Downloading {recipe['repo_id']}",
                "error": None,
            }
        )

    fetch = fetcher or _default_fetcher
    local_dir = Path(recipe["local_dir"]())

    def _run() -> None:
        def on_progress(done: int, total: int | None) -> None:
            _set(bytes_downloaded=done, bytes_total=total, message="Downloading model files")

        try:
            fetch(recipe["repo_id"], local_dir, on_progress)
        except Exception as exc:  # noqa: BLE001 - surface download failures to the UI
            _set(status="failed", error=str(exc), message="Download failed")
            return
        _set(status="succeeded", message="Download complete", error=None)

    if background:
        threading.Thread(target=_run, name=f"model-download-{model_id}", daemon=True).start()
    else:
        _run()
    return status()
