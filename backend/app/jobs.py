from __future__ import annotations

import asyncio
import json
import queue
import threading
import time
import urllib.error
import urllib.request
from typing import Any, Callable
from uuid import uuid4

from app import config, db, images as image_store
from app import logging_utils
from app.status_copy import with_status_copy
from inference.base import EditParams, GenerationParams
from inference.manager import get_manager


_JOB_QUEUE: queue.Queue[str] = queue.Queue()
_SUBSCRIBERS: dict[str, list[queue.Queue[dict[str, Any]]]] = {}
_SUBSCRIBERS_LOCK = threading.Lock()
_WORKERS_STARTED = False
_GPU_SEMAPHORE = threading.Semaphore(max(config.MAX_CONCURRENT_JOBS, 1))
_CURRENT_JOB_ID: str | None = None
_CURRENT_JOB_LOCK = threading.Lock()


def _now_ms() -> int:
    return int(time.time() * 1000)


def _publish(job_id: str, event: str, data: dict[str, Any]) -> None:
    with _SUBSCRIBERS_LOCK:
        subscribers = list(_SUBSCRIBERS.get(job_id, []))
    for subscriber in subscribers:
        subscriber.put({"event": event, "data": data})


def publish_event(job_id: str, event: str, data: dict[str, Any]) -> None:
    if event == "status":
        _update_job_activity(job_id, status=data.get("status"), stage=data.get("stage"))
    elif event == "stage":
        _update_job_activity(job_id, stage=data.get("stage"))
    elif event == "progress":
        _update_job_activity(
            job_id,
            progress_percent=data.get("percent"),
            progress_step=data.get("step"),
            progress_total=data.get("total_steps"),
        )
    _publish(job_id, event, data)


def subscribe(job_id: str) -> queue.Queue[dict[str, Any]]:
    subscriber: queue.Queue[dict[str, Any]] = queue.Queue()
    with _SUBSCRIBERS_LOCK:
        _SUBSCRIBERS.setdefault(job_id, []).append(subscriber)
    return subscriber


def unsubscribe(job_id: str, subscriber: queue.Queue[dict[str, Any]]) -> None:
    with _SUBSCRIBERS_LOCK:
        queues = _SUBSCRIBERS.get(job_id, [])
        if subscriber in queues:
            queues.remove(subscriber)
        if not queues and job_id in _SUBSCRIBERS:
            _SUBSCRIBERS.pop(job_id, None)


def format_sse(event: str, data: dict[str, Any]) -> str:
    payload = json.dumps(data)
    return f"event: {event}\ndata: {payload}\n\n"


def _job_activity_payload(job: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "last_activity_at": job.get("last_activity_at"),
    }
    if job.get("stage") is not None:
        payload["stage"] = job.get("stage")
    if job.get("progress_percent") is not None:
        payload["percent"] = job.get("progress_percent")
    if job.get("progress_step") is not None:
        payload["step"] = job.get("progress_step")
    if job.get("progress_total") is not None:
        payload["total_steps"] = job.get("progress_total")
    return {key: value for key, value in payload.items() if value is not None}


def _update_job_activity(
    job_id: str,
    *,
    status: str | None = None,
    stage: str | None = None,
    progress_percent: int | None = None,
    progress_step: int | None = None,
    progress_total: int | None = None,
    started_at: int | None = None,
    finished_at: int | None = None,
    error: str | None = None,
) -> int:
    last_activity_at = _now_ms()
    fields: dict[str, Any] = {"last_activity_at": last_activity_at}
    if status is not None:
        fields["status"] = status
    if stage is not None:
        fields["stage"] = stage
    if progress_percent is not None:
        fields["progress_percent"] = progress_percent
    if progress_step is not None:
        fields["progress_step"] = progress_step
    if progress_total is not None:
        fields["progress_total"] = progress_total
    if started_at is not None:
        fields["started_at"] = started_at
    if finished_at is not None:
        fields["finished_at"] = finished_at
    if error is not None:
        fields["error"] = error

    assignments = ", ".join(f"{column} = ?" for column in fields)
    values = list(fields.values())
    values.append(job_id)
    with db.get_connection() as conn:
        conn.execute(f"UPDATE jobs SET {assignments} WHERE id = ?", values)
        conn.commit()
    return last_activity_at


def init_jobs() -> None:
    global _WORKERS_STARTED
    if _WORKERS_STARTED:
        return
    db.init_db()
    recover_interrupted_jobs()
    if config.INFERENCE_MODE == "local":
        _start_workers()
    _WORKERS_STARTED = True


def recover_interrupted_jobs() -> dict[str, int]:
    now = _now_ms()
    with db.get_connection() as conn:
        running_rows = conn.execute(
            "SELECT id FROM jobs WHERE status = ?",
            ("running",),
        ).fetchall()
        queued_rows = conn.execute(
            "SELECT id FROM jobs WHERE status = ?",
            ("queued",),
        ).fetchall()
        conn.execute(
            """
            UPDATE jobs
            SET status = ?, finished_at = ?, error = ?, stage = ?, last_activity_at = ?
            WHERE status IN (?, ?)
            """,
            ("failed", now, "server restarted", "failed", now, "running", "queued"),
        )
        conn.commit()

    recovered = {
        "queued": len(queued_rows),
        "running": len(running_rows),
        "marked_failed": len(running_rows) + len(queued_rows),
    }
    from app import orchestration

    for row in list(running_rows) + list(queued_rows):
        orchestration.finish_open_attempts(
            row["id"],
            status="failed",
            failure_type="process_restart",
            retryable=False,
            message="server restarted",
        )
    if running_rows or queued_rows:
        logging_utils.log_event(
            "job_recovery",
            recovered_queued=recovered["queued"],
            recovered_running=recovered["running"],
            marked_failed=recovered["marked_failed"],
        )
    return recovered


def _start_workers() -> None:
    worker_count = max(config.MAX_CONCURRENT_JOBS, 1)
    for idx in range(worker_count):
        worker = threading.Thread(target=_worker_loop, name=f"job-worker-{idx}", daemon=True)
        worker.start()


def _validate_limits(job_type: str, params: GenerationParams | EditParams) -> None:
    if params.steps > config.MAX_STEPS:
        raise ValueError(f"steps exceeds MAX_STEPS={config.MAX_STEPS}")
    if job_type == "t2i":
        assert isinstance(params, GenerationParams)
        if params.width > config.MAX_WIDTH or params.height > config.MAX_HEIGHT:
            raise ValueError(
                f"resolution exceeds MAX_WIDTH={config.MAX_WIDTH} or MAX_HEIGHT={config.MAX_HEIGHT}"
            )


def _dispatch_to_worker(job_id: str) -> None:
    url = config.WORKER_URL.rstrip("/") + "/worker/run"
    payload = json.dumps({"job_id": job_id}).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if config.WORKER_TOKEN:
        headers["Authorization"] = f"Bearer {config.WORKER_TOKEN}"
    request = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            if response.status >= 400:
                raise RuntimeError(f"Worker responded with status {response.status}.")
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Worker dispatch failed: {exc}") from exc


def submit_job(job_type: str, model_id: str, params: GenerationParams | EditParams) -> str:
    _validate_limits(job_type, params)

    try:
        runner = get_manager().get_runner(model_id)
    except KeyError as exc:
        raise ValueError(str(exc)) from exc

    if job_type == "t2i" and "t2i" not in runner.capabilities:
        raise ValueError("Model does not support text-to-image.")
    if job_type == "edit" and "edit" not in runner.capabilities:
        raise ValueError("Model does not support image editing.")

    status = runner.model_status()
    if not status.get("present", True):
        message = f"Model files missing for '{model_id}'. Check local assets and try again."
        if status.get("detail"):
            message = f"{message} {status['detail']}"
        raise ValueError(message)

    if job_type == "edit" and isinstance(params, EditParams):
        for image_id in params.image_ids:
            if not image_store.get_image_path(image_id).exists():
                raise ValueError(f"Input image '{image_id}' not found.")

    job_id = uuid4().hex
    run_id = uuid4().hex
    created_at = _now_ms()

    input_image_ids = None
    width = None
    height = None
    negative_prompt = None
    strength = None
    if isinstance(params, GenerationParams):
        width = params.width
        height = params.height
        negative_prompt = params.negative_prompt
        input_image_ids = json.dumps([])
    if isinstance(params, EditParams):
        input_image_ids = json.dumps(params.image_ids)
        strength = params.strength

    with db.get_connection() as conn:
        conn.execute(
            """
            INSERT INTO jobs (
                id, type, status, created_at, started_at, finished_at, error,
                stage, progress_percent, progress_step, progress_total, last_activity_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (job_id, job_type, "queued", created_at, None, None, None, "queued", 0, 0, None, created_at),
        )
        conn.execute(
            """
            INSERT INTO runs (
                id, job_id, model_id, prompt, negative_prompt, seed, steps,
                width, height, guidance_scale, true_cfg_scale,
                strength, input_image_ids, output_image_id, pending_output_image_id,
                latency_ms
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                job_id,
                model_id,
                params.prompt,
                negative_prompt,
                params.seed,
                params.steps,
                width,
                height,
                params.guidance_scale,
                params.true_cfg_scale,
                strength,
                input_image_ids,
                None,
                None,
                None,
            ),
        )
        conn.commit()

    if config.INFERENCE_MODE == "worker":
        try:
            _dispatch_to_worker(job_id)
        except Exception as exc:
            _mark_job_failed(job_id, str(exc))
            raise
    else:
        _JOB_QUEUE.put(job_id)
    _publish(
        job_id,
        "status",
        {"status": "queued", "stage": "queued", "last_activity_at": created_at},
    )
    return job_id


def _worker_loop() -> None:
    while True:
        job_id = _JOB_QUEUE.get()
        if job_id is None:
            continue
        try:
            run_job(job_id)
        except Exception as exc:
            _mark_job_failed(job_id, str(exc))
        finally:
            _JOB_QUEUE.task_done()


def run_job(
    job_id: str,
    publish: Callable[[str, str, dict[str, Any]], None] | None = None,
) -> None:
    global _CURRENT_JOB_ID
    publish_fn = publish or _publish
    job = get_job(job_id)
    if not job:
        return

    started_at = _now_ms()
    job_started = time.perf_counter()
    with _CURRENT_JOB_LOCK:
        _CURRENT_JOB_ID = job_id

    def _publish_stage(stage: str) -> None:
        last_activity_at = _update_job_activity(job_id, stage=stage)
        publish_fn(
            job_id,
            "stage",
            {
                "stage": stage,
                "elapsed_ms": int((time.perf_counter() - job_started) * 1000),
                "last_activity_at": last_activity_at,
            },
        )

    last_activity_at = _update_job_activity(
        job_id,
        status="running",
        stage="loading",
        progress_percent=0,
        progress_step=0,
        started_at=started_at,
    )
    from app import orchestration

    attempt = orchestration.begin_attempt(job_id, execution_mode=config.INFERENCE_MODE)
    attempt_id = attempt["id"]
    publish_fn(
        job_id,
        "status",
        {"status": "running", "stage": "loading", "last_activity_at": last_activity_at},
    )
    _publish_stage("loading")

    run = job.get("run")
    if not run:
        raise RuntimeError("Run metadata missing for job.")

    manager = get_manager()
    runner = manager.get_runner(run["model_id"])
    prompt_value = run.get("prompt") or ""
    log_payload = {
        "job_id": job_id,
        "run_id": run["id"],
        "type": job["type"],
        "model_id": run["model_id"],
        "prompt_len": len(prompt_value),
        "seed": run["seed"],
        "steps": run["steps"],
        "width": run.get("width"),
        "height": run.get("height"),
        "guidance_scale": run.get("guidance_scale"),
        "true_cfg_scale": run.get("true_cfg_scale"),
        "strength": run.get("strength"),
        "device": runner.device,
        "dtype": str(runner.dtype),
    }
    backend_name = getattr(runner, "backend_name", None)
    if backend_name:
        log_payload["engine_backend"] = backend_name
    if config.DEBUG:
        log_payload["prompt"] = prompt_value
    logging_utils.log_event("job_start", **log_payload)

    def progress_callback(step: int, total_steps: int) -> None:
        percent = int((step / total_steps) * 100) if total_steps else 0
        last_activity_at = _update_job_activity(
            job_id,
            progress_percent=percent,
            progress_step=step,
            progress_total=total_steps,
        )
        orchestration.heartbeat(attempt_id)
        publish_fn(
            job_id,
            "progress",
            {
                "step": step,
                "total_steps": total_steps,
                "percent": percent,
                "elapsed_ms": int((time.perf_counter() - job_started) * 1000),
                "last_activity_at": last_activity_at,
            },
        )

    _GPU_SEMAPHORE.acquire()
    try:
        runner.load()
        _publish_stage("running")

        start = time.perf_counter()
        try:
            if job["type"] == "t2i":
                params = GenerationParams(
                    prompt=run["prompt"],
                    negative_prompt=run["negative_prompt"],
                    seed=run["seed"],
                    steps=run["steps"],
                    width=run["width"],
                    height=run["height"],
                    guidance_scale=run["guidance_scale"],
                    true_cfg_scale=run["true_cfg_scale"],
                )
                image = runner.generate(params, progress_callback=progress_callback)
            elif job["type"] == "edit":
                params = EditParams(
                    prompt=run["prompt"],
                    image_ids=run["input_image_ids"],
                    seed=run["seed"],
                    steps=run["steps"],
                    guidance_scale=run["guidance_scale"],
                    true_cfg_scale=run["true_cfg_scale"],
                    strength=run.get("strength"),
                )
                image = runner.edit(params, progress_callback=progress_callback)
            else:
                raise RuntimeError(f"Unknown job type '{job['type']}'.")
        except Exception as exc:
            raise RuntimeError(str(exc)) from exc

        _publish_stage("saving")
        image_id, _ = image_store.save_image(
            image,
            source="job",
            job_id=job_id,
            run_id=run["id"],
        )
        latency_ms = int((time.perf_counter() - start) * 1000)
    finally:
        _GPU_SEMAPHORE.release()
        with _CURRENT_JOB_LOCK:
            _CURRENT_JOB_ID = None

    finished_at = _now_ms()

    review_required = runner.manual_review and config.SAFETY_REVIEW_MODE == "manual"
    with db.get_connection() as conn:
        if review_required:
            conn.execute(
                "UPDATE runs SET pending_output_image_id = ?, latency_ms = ? WHERE job_id = ?",
                (image_id, latency_ms, job_id),
            )
            conn.execute(
                """
                UPDATE jobs
                SET status = ?, finished_at = ?, stage = ?, progress_percent = ?,
                    last_activity_at = ?
                WHERE id = ?
                """,
                ("pending_review", finished_at, "review", 100, finished_at, job_id),
            )
        else:
            conn.execute(
                "UPDATE runs SET output_image_id = ?, latency_ms = ? WHERE job_id = ?",
                (image_id, latency_ms, job_id),
            )
            conn.execute(
                """
                UPDATE jobs
                SET status = ?, finished_at = ?, stage = ?, progress_percent = ?,
                    last_activity_at = ?
                WHERE id = ?
                """,
                ("succeeded", finished_at, "complete", 100, finished_at, job_id),
            )
        conn.commit()

    from app import orchestration

    if review_required:
        orchestration.finish_open_attempts(
            job_id,
            status="succeeded",
            temp_output_image_id=image_id,
        )
    else:
        orchestration.finish_open_attempts(
            job_id,
            status="succeeded",
            output_image_id=image_id,
        )

    if review_required:
        publish_fn(
            job_id,
            "status",
            {"status": "pending_review", "stage": "review", "last_activity_at": finished_at},
        )
        publish_fn(
            job_id,
            "review_required",
            {"message": "Manual review required.", "last_activity_at": finished_at},
        )
        logging_utils.log_event(
            "job_pending_review",
            job_id=job_id,
            run_id=run["id"],
            latency_ms=latency_ms,
        )
        return

    publish_fn(
        job_id,
        "status",
        {"status": "succeeded", "stage": "complete", "last_activity_at": finished_at},
    )
    publish_fn(
        job_id,
        "result",
        {"output_image_id": image_id, "latency_ms": latency_ms, "last_activity_at": finished_at},
    )
    logging_utils.log_event(
        "job_success",
        job_id=job_id,
        run_id=run["id"],
        output_image_id=image_id,
        latency_ms=latency_ms,
    )


def _mark_job_failed(
    job_id: str,
    message: str,
    publish: Callable[[str, str, dict[str, Any]], None] | None = None,
) -> None:
    global _CURRENT_JOB_ID
    publish_fn = publish or _publish
    job = get_job(job_id) or {}
    run = job.get("run") or {}
    finished_at = _now_ms()
    with db.get_connection() as conn:
        conn.execute(
            """
            UPDATE jobs
            SET status = ?, finished_at = ?, error = ?, stage = ?, last_activity_at = ?
            WHERE id = ?
            """,
            ("failed", finished_at, message, "failed", finished_at, job_id),
        )
        conn.commit()
    from app import orchestration

    failure_type, retryable = orchestration.classify_failure(message)
    orchestration.finish_open_attempts(
        job_id,
        status="failed",
        failure_type=failure_type,
        retryable=retryable,
        message=message,
    )
    with _CURRENT_JOB_LOCK:
        global _CURRENT_JOB_ID
        if _CURRENT_JOB_ID == job_id:
            _CURRENT_JOB_ID = None
    publish_fn(
        job_id,
        "status",
        {"status": "failed", "stage": "failed", "last_activity_at": finished_at},
    )
    publish_fn(job_id, "error", {"message": message, "last_activity_at": finished_at})
    logging_utils.log_error(
        "job_failed",
        job_id=job_id,
        run_id=run.get("id"),
        error=message,
    )


def mark_job_failed(
    job_id: str,
    message: str,
    publish: Callable[[str, str, dict[str, Any]], None] | None = None,
) -> None:
    _mark_job_failed(job_id, message, publish=publish)


def get_queue_length() -> int:
    return _JOB_QUEUE.qsize()


def get_current_job_id() -> str | None:
    with _CURRENT_JOB_LOCK:
        return _CURRENT_JOB_ID


def get_run(run_id: str) -> dict[str, Any] | None:
    with db.get_connection() as conn:
        row = conn.execute(
            """
            SELECT runs.*, jobs.status, jobs.created_at, jobs.finished_at, jobs.type, jobs.error
            FROM runs
            JOIN jobs ON jobs.id = runs.job_id
            WHERE runs.id = ?
            """,
            (run_id,),
        ).fetchone()
    if not row:
        return None
    entry = dict(row)
    if entry.get("input_image_ids"):
        entry["input_image_ids"] = json.loads(entry["input_image_ids"])
    return with_status_copy(entry)


def get_recent_latencies(limit: int = 50) -> list[int]:
    with db.get_connection() as conn:
        rows = conn.execute(
            """
            SELECT runs.latency_ms
            FROM runs
            JOIN jobs ON jobs.id = runs.job_id
            WHERE runs.latency_ms IS NOT NULL
            ORDER BY jobs.created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [row["latency_ms"] for row in rows if row["latency_ms"] is not None]


def get_job(job_id: str) -> dict[str, Any] | None:
    with db.get_connection() as conn:
        job_row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        if not job_row:
            return None
        run_row = conn.execute("SELECT * FROM runs WHERE job_id = ?", (job_id,)).fetchone()

    job = dict(job_row)
    run = dict(run_row) if run_row else None
    if run and run.get("input_image_ids"):
        run["input_image_ids"] = json.loads(run["input_image_ids"])
    if run:
        run["type"] = job["type"]
        run["status"] = job["status"]
        run["error"] = job.get("error")
        run = with_status_copy(run)
    from app import orchestration

    attempts = orchestration.list_attempts(job_id)
    return with_status_copy({**job, "run": run, "attempts": attempts})


def list_runs(limit: int = 50, status: str | None = None) -> list[dict[str, Any]]:
    with db.get_connection() as conn:
        query = (
            "SELECT runs.*, jobs.status, jobs.created_at, jobs.finished_at, jobs.type, jobs.error "
            "FROM runs "
            "JOIN jobs ON jobs.id = runs.job_id "
        )
        params: list[Any] = []
        if status:
            query += "WHERE jobs.status = ? "
            params.append(status)
        query += "ORDER BY jobs.created_at DESC LIMIT ?"
        params.append(limit)
        rows = conn.execute(query, params).fetchall()

    runs = []
    for row in rows:
        entry = dict(row)
        if entry.get("input_image_ids"):
            entry["input_image_ids"] = json.loads(entry["input_image_ids"])
        runs.append(with_status_copy(entry))
    return runs


def delete_run(run_id: str, delete_images: bool = False) -> bool:
    with db.get_connection() as conn:
        row = conn.execute(
            "SELECT job_id, output_image_id, pending_output_image_id FROM runs WHERE id = ?",
            (run_id,),
        ).fetchone()
        if not row:
            return False
        job_id = row["job_id"]
        output_image_id = row["output_image_id"]
        pending_image_id = row["pending_output_image_id"]
        conn.execute("DELETE FROM runs WHERE id = ?", (run_id,))
        conn.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
        conn.commit()
    if delete_images:
        if output_image_id:
            image_store.delete_image(output_image_id)
        if pending_image_id and pending_image_id != output_image_id:
            image_store.delete_image(pending_image_id)
    return True


def delete_runs(
    status: str | None = None,
    limit: int | None = None,
    delete_images: bool = False,
) -> int:
    if not status and not limit:
        raise ValueError("Provide status or limit to delete runs.")
    if status in {"queued", "running"}:
        raise ValueError("Cannot delete active runs.")

    query = (
        "SELECT runs.id "
        "FROM runs "
        "JOIN jobs ON jobs.id = runs.job_id "
    )
    params: list[Any] = []
    if status:
        query += "WHERE jobs.status = ? "
        params.append(status)
    else:
        query += "WHERE jobs.status NOT IN (?, ?) "
        params.extend(["queued", "running"])
    query += "ORDER BY jobs.created_at DESC "
    if limit:
        query += "LIMIT ?"
        params.append(limit)

    with db.get_connection() as conn:
        rows = conn.execute(query, params).fetchall()

    deleted = 0
    for row in rows:
        if delete_run(row["id"], delete_images=delete_images):
            deleted += 1
    return deleted


def reveal_job(job_id: str) -> str:
    job = get_job(job_id)
    if not job:
        raise ValueError("Job not found.")
    if job.get("status") != "pending_review":
        raise ValueError("Job is not awaiting review.")
    run = job.get("run") or {}

    with db.get_connection() as conn:
        row = conn.execute(
            "SELECT pending_output_image_id FROM runs WHERE job_id = ?",
            (job_id,),
        ).fetchone()
        if not row or not row["pending_output_image_id"]:
            raise ValueError("No pending image to reveal.")
        image_id = row["pending_output_image_id"]
        conn.execute(
            "UPDATE runs SET output_image_id = ?, pending_output_image_id = NULL WHERE job_id = ?",
            (image_id, job_id),
        )
        now = _now_ms()
        conn.execute(
            """
            UPDATE jobs
            SET status = ?, stage = ?, progress_percent = ?, last_activity_at = ?
            WHERE id = ?
            """,
            ("succeeded", "complete", 100, now, job_id),
        )
        conn.commit()

    _publish(job_id, "status", {"status": "succeeded", "stage": "complete", "last_activity_at": now})
    _publish(job_id, "result", {"output_image_id": image_id, "last_activity_at": now})
    logging_utils.log_event(
        "job_revealed",
        job_id=job_id,
        run_id=run.get("id"),
        output_image_id=image_id,
    )
    return image_id


def stream_events(job_id: str, request: Any | None = None) -> Any:
    async def generator() -> Any:
        job = get_job(job_id)
        if not job:
            yield format_sse("error", {"message": "Job not found."})
            return

        yield format_sse(
            "status",
            {"status": job["status"], **_job_activity_payload(job)},
        )
        if job.get("stage"):
            yield format_sse("stage", {"stage": job["stage"], **_job_activity_payload(job)})
        if job.get("progress_percent") is not None:
            yield format_sse("progress", _job_activity_payload(job))
        if job["status"] == "pending_review":
            yield format_sse(
                "review_required",
                {"message": "Manual review required.", **_job_activity_payload(job)},
            )
            return
        if job["status"] == "succeeded" and job.get("run"):
            output_image_id = job["run"].get("output_image_id")
            if output_image_id:
                yield format_sse(
                    "result",
                    {"output_image_id": output_image_id, **_job_activity_payload(job)},
                )
                return
        if job["status"] == "failed":
            yield format_sse("error", {"message": job.get("error"), **_job_activity_payload(job)})
            return

        subscriber = subscribe(job_id)
        try:
            while True:
                if request is not None:
                    try:
                        if await request.is_disconnected():
                            break
                    except Exception:
                        pass
                try:
                    event = await asyncio.to_thread(subscriber.get, True, 5)
                except queue.Empty:
                    yield ": keep-alive\n\n"
                    continue
                yield format_sse(event["event"], event["data"])
                if event["event"] in {"result", "error", "review_required"}:
                    break
        finally:
            unsubscribe(job_id, subscriber)

    return generator()
