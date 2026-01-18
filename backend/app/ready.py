from __future__ import annotations

import threading
from typing import Any


_LOCK = threading.Lock()
_STATE: dict[str, Any] = {
    "ready": False,
    "status": "starting",
    "details": {},
}


def set_state(ready: bool, status: str, details: dict | None = None) -> None:
    with _LOCK:
        _STATE["ready"] = ready
        _STATE["status"] = status
        _STATE["details"] = details or {}


def get_state() -> dict[str, Any]:
    with _LOCK:
        return dict(_STATE)
