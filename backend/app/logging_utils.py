from __future__ import annotations

import json
import logging
import time
import traceback
from typing import Any

from app import config

logger = logging.getLogger("ai_image_edit")


def setup_logging() -> None:
    level = logging.DEBUG if config.DEBUG else logging.INFO
    logging.basicConfig(level=level, format="%(message)s")


def log_event(event: str, **fields: Any) -> None:
    payload = {
        "event": event,
        "ts": int(time.time() * 1000),
        **fields,
    }
    logger.info(json.dumps(payload, ensure_ascii=True))


def log_error(event: str, **fields: Any) -> None:
    payload = {
        "event": event,
        "ts": int(time.time() * 1000),
        **fields,
    }
    logger.error(json.dumps(payload, ensure_ascii=True))


def log_exception(event: str, exc: Exception, **fields: Any) -> None:
    payload = {
        "event": event,
        "ts": int(time.time() * 1000),
        "error": f"{exc.__class__.__name__}: {exc}",
        "traceback": traceback.format_exc(),
        **fields,
    }
    logger.error(json.dumps(payload, ensure_ascii=True))
