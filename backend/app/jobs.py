from __future__ import annotations

import json
import queue
import threading
import time
from typing import Any
from uuid import uuid4

from app import config, db, images as image_store
from app import logging_utils
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


def init_jobs() -> None:
    global _WORKERS_STARTED
    if _WORKERS_STARTED:
        return
    db.init_db()
    _recover_jobs()
    _start_workers()
    _WORKERS_STARTED = True


def _recover_jobs() -> None:
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
            "UPDATE jobs SET status = ?, finished_at = ?, error = ? WHERE status IN (?, ?)",
            ("failed", now, "server restarted", "running", "queued"),
        )
        conn.commit()

    if running_rows or queued_rows:
        logging_utils.log_event(
            "job_recovery",
            recovered_queued=0,
            marked_failed=len(running_rows) + len(queued_rows),
        )


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
    if isinstance(params, GenerationParams):
        width = params.width
        height = params.height
        negative_prompt = params.negative_prompt
        input_image_ids = json.dumps([])
    if isinstance(params, EditParams):
        input_image_ids = json.dumps(params.image_ids)

    with db.get_connection() as conn:
        conn.execute(
            """
            INSERT INTO jobs (id, type, status, created_at, started_at, finished_at, error)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (job_id, job_type, "queued", created_at, None, None, None),
        )
        conn.execute(
            """
            INSERT INTO runs (
                id, job_id, model_id, prompt, negative_prompt, seed, steps,
                width, height, guidance_scale, true_cfg_scale,
                input_image_ids, output_image_id, latency_ms
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                input_image_ids,
                None,
                None,
            ),
        )
        conn.commit()

    _JOB_QUEUE.put(job_id)
    _publish(job_id, "status", {"status": "queued"})
    return job_id


def _worker_loop() -> None:
    while True:
        job_id = _JOB_QUEUE.get()
        if job_id is None:
            continue
        try:
            _run_job(job_id)
        except Exception as exc:
            _mark_job_failed(job_id, str(exc))
        finally:
            _JOB_QUEUE.task_done()


def _run_job(job_id: str) -> None:
    global _CURRENT_JOB_ID
    job = get_job(job_id)
    if not job:
        return

    started_at = _now_ms()
    with _CURRENT_JOB_LOCK:
        _CURRENT_JOB_ID = job_id
    with db.get_connection() as conn:
        conn.execute(
            "UPDATE jobs SET status = ?, started_at = ? WHERE id = ?",
            ("running", started_at, job_id),
        )
        conn.commit()
    _publish(job_id, "status", {"status": "running"})
    _publish(job_id, "stage", {"stage": "loading"})

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
        "device": runner.device,
        "dtype": str(runner.dtype),
    }
    if config.DEBUG:
        log_payload["prompt"] = prompt_value
    logging_utils.log_event("job_start", **log_payload)

    def progress_callback(step: int, total_steps: int) -> None:
        percent = int((step / total_steps) * 100)
        _publish(job_id, "progress", {"step": step, "total_steps": total_steps, "percent": percent})

    _GPU_SEMAPHORE.acquire()
    try:
        runner.load()
        _publish(job_id, "stage", {"stage": "running"})

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
                )
                image = runner.edit(params, progress_callback=progress_callback)
            else:
                raise RuntimeError(f"Unknown job type '{job['type']}'.")
        except Exception as exc:
            raise RuntimeError(str(exc)) from exc

        _publish(job_id, "stage", {"stage": "saving"})
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

    with db.get_connection() as conn:
        conn.execute(
            "UPDATE runs SET output_image_id = ?, latency_ms = ? WHERE job_id = ?",
            (image_id, latency_ms, job_id),
        )
        conn.execute(
            "UPDATE jobs SET status = ?, finished_at = ? WHERE id = ?",
            ("succeeded", finished_at, job_id),
        )
        conn.commit()

    _publish(job_id, "status", {"status": "succeeded"})
    _publish(
        job_id,
        "result",
        {"output_image_id": image_id, "latency_ms": latency_ms},
    )
    logging_utils.log_event(
        "job_success",
        job_id=job_id,
        run_id=run["id"],
        output_image_id=image_id,
        latency_ms=latency_ms,
    )


def _mark_job_failed(job_id: str, message: str) -> None:
    global _CURRENT_JOB_ID
    job = get_job(job_id) or {}
    run = job.get("run") or {}
    finished_at = _now_ms()
    with db.get_connection() as conn:
        conn.execute(
            "UPDATE jobs SET status = ?, finished_at = ?, error = ? WHERE id = ?",
            ("failed", finished_at, message, job_id),
        )
        conn.commit()
    with _CURRENT_JOB_LOCK:
        global _CURRENT_JOB_ID
        if _CURRENT_JOB_ID == job_id:
            _CURRENT_JOB_ID = None
    _publish(job_id, "status", {"status": "failed"})
    _publish(job_id, "error", {"message": message})
    logging_utils.log_error(
        "job_failed",
        job_id=job_id,
        run_id=run.get("id"),
        error=message,
    )


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
    return entry


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
    return {**job, "run": run}


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
        runs.append(entry)
    return runs


def stream_events(job_id: str) -> Any:
    def generator() -> Any:
        job = get_job(job_id)
        if not job:
            yield format_sse("error", {"message": "Job not found."})
            return

        yield format_sse("status", {"status": job["status"]})
        if job["status"] == "succeeded" and job.get("run"):
            output_image_id = job["run"].get("output_image_id")
            if output_image_id:
                yield format_sse("result", {"output_image_id": output_image_id})
                return
        if job["status"] == "failed":
            yield format_sse("error", {"message": job.get("error")})
            return

        subscriber = subscribe(job_id)
        try:
            while True:
                try:
                    event = subscriber.get(timeout=15)
                except queue.Empty:
                    yield ": keep-alive\n\n"
                    continue
                yield format_sse(event["event"], event["data"])
                if event["event"] in {"result", "error"}:
                    break
        finally:
            unsubscribe(job_id, subscriber)

    return generator()
