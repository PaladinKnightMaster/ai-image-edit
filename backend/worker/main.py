from __future__ import annotations

import json
import queue
import threading
import urllib.error
import urllib.request
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

from app import config, db, jobs, logging_utils

logging_utils.setup_logging()

app = FastAPI(title="ai-image-edit-worker")

_JOB_QUEUE: queue.Queue[str] = queue.Queue()
_WORKER_STARTED = False


class RunRequest(BaseModel):
    job_id: str


def _publish_to_api(job_id: str, event: str, data: dict[str, Any]) -> None:
    url = config.WORKER_CALLBACK_URL.rstrip("/") + f"/api/internal/jobs/{job_id}/event"
    payload = json.dumps({"event": event, "data": data}).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if config.WORKER_TOKEN:
        headers["Authorization"] = f"Bearer {config.WORKER_TOKEN}"
    request = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=5):
            pass
    except urllib.error.URLError as exc:
        logging_utils.log_error("worker_publish_failed", job_id=job_id, error=str(exc))


def _worker_loop() -> None:
    while True:
        job_id = _JOB_QUEUE.get()
        if not job_id:
            continue
        try:
            jobs.run_job(job_id, publish=_publish_to_api)
        except Exception as exc:
            jobs.mark_job_failed(job_id, str(exc), publish=_publish_to_api)
        finally:
            _JOB_QUEUE.task_done()


def _start_worker() -> None:
    global _WORKER_STARTED
    if _WORKER_STARTED:
        return
    worker = threading.Thread(target=_worker_loop, name="inference-worker", daemon=True)
    worker.start()
    _WORKER_STARTED = True


@app.on_event("startup")
def _startup() -> None:
    db.init_db()
    _start_worker()


@app.post("/worker/run")
def submit_job(
    request: RunRequest,
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:
    if config.WORKER_TOKEN:
        expected = f"Bearer {config.WORKER_TOKEN}"
        if authorization != expected:
            raise HTTPException(status_code=401, detail="unauthorized")
    _JOB_QUEUE.put(request.job_id)
    return {"queued": True}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
