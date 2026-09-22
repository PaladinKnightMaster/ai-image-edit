"""Where the recommended local model is stored.

Ollama keeps one models directory. The default is suggested, the user confirms
it once, and later downloads reuse that choice. An explicit SDXL_OV_BASE_DIR
environment value wins and the UI must not override it.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from app import config

_store_path: Path | None = None


def store_path() -> Path:
    if _store_path is not None:
        return _store_path
    return config.REPO_ROOT / "data" / "model_location.json"


def set_store_path(path: Path | None) -> None:
    global _store_path
    _store_path = path


def default_dir() -> Path:
    return (config.REPO_ROOT / "models" / "openvino" / "sdxl_base").resolve()


def locked_by_env() -> bool:
    return bool(os.environ.get("SDXL_OV_BASE_DIR"))


def _read_saved() -> dict[str, Any]:
    path = store_path()
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _write_saved(payload: dict[str, Any]) -> None:
    path = store_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _resolve_user_path(raw: str) -> Path:
    text = (raw or "").strip()
    if not text:
        raise ValueError("Choose a folder for the model.")
    path = Path(text)
    if not path.is_absolute():
        path = config.REPO_ROOT / path
    path = path.resolve()
    if path.exists() and not path.is_dir():
        raise ValueError("That path is a file. Choose a folder.")
    return path


def apply_effective_dir() -> Path:
    """Point the running process at the effective SDXL folder."""
    location = describe()
    config.SDXL_OV_BASE_DIR = Path(location["path"])
    return config.SDXL_OV_BASE_DIR


def describe() -> dict[str, Any]:
    fallback = default_dir()
    saved = _read_saved()
    saved_path = str(saved.get("path") or "").strip()
    confirmed = bool(saved.get("confirmed")) and bool(saved_path)
    if locked_by_env():
        path = _resolve_user_path(os.environ["SDXL_OV_BASE_DIR"])
        confirmed = True
        source = "env"
    elif confirmed:
        path = _resolve_user_path(saved_path)
        source = "settings"
    else:
        path = fallback
        source = "default"
    return {
        "model_id": "sdxl-openvino",
        "path": str(path),
        "default_path": str(fallback),
        "confirmed": confirmed,
        "locked_by_env": locked_by_env(),
        "source": source,
        "exists": path.exists(),
    }


def confirm(raw_path: str) -> dict[str, Any]:
    if locked_by_env():
        raise ValueError("SDXL_OV_BASE_DIR is set. The app uses that folder and cannot change it here.")
    path = _resolve_user_path(raw_path)
    _write_saved({"path": str(path), "confirmed": True})
    apply_effective_dir()
    return describe()
