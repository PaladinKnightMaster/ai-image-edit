"""Local SQLite job orchestration: append-only attempt history.

Cancellation, automatic retry, and restart requeue stay in later tickets.
This module only records one attempt per execution and closes it honestly.
"""

from __future__ import annotations

import socket
from typing import Any
from uuid import uuid4

from app import config, db


LEASE_MS = 120_000


def _clock() -> int:
    from app import jobs

    return jobs._now_ms()


def classify_failure(message: str) -> tuple[str, bool]:
    """Return (failure_type, retryable). Retry stays false until WR5-006."""
    lowered = (message or "").lower()
    if "server restarted" in lowered or "process restart" in lowered:
        return "process_restart", False
    if "not found" in lowered or "missing" in lowered or "does not support" in lowered:
        return "invalid_input", False
    if "out of memory" in lowered or "cuda out of memory" in lowered:
        return "out_of_memory", False
    return "execution_error", False


def worker_id() -> str:
    return f"{socket.gethostname()}:{config.INFERENCE_MODE}"


def begin_attempt(job_id: str, *, execution_mode: str | None = None) -> dict[str, Any]:
    started_at = _clock()
    with db.get_connection() as conn:
        row = conn.execute(
            "SELECT COALESCE(MAX(attempt_number), 0) AS n FROM job_attempts WHERE job_id = ?",
            (job_id,),
        ).fetchone()
        attempt_number = int(row["n"]) + 1
        attempt_id = uuid4().hex
        conn.execute(
            """
            INSERT INTO job_attempts (
                id, job_id, attempt_number, worker_id, execution_mode, status,
                lease_expires_at, last_heartbeat_at, started_at, retryable
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                attempt_id,
                job_id,
                attempt_number,
                worker_id(),
                execution_mode or config.INFERENCE_MODE,
                "running",
                started_at + LEASE_MS,
                started_at,
                started_at,
                0,
            ),
        )
        conn.commit()
    return get_attempt(attempt_id) or {"id": attempt_id, "job_id": job_id}


def heartbeat(attempt_id: str) -> None:
    now = _clock()
    with db.get_connection() as conn:
        conn.execute(
            """
            UPDATE job_attempts
            SET last_heartbeat_at = ?, lease_expires_at = ?
            WHERE id = ? AND status = 'running'
            """,
            (now, now + LEASE_MS, attempt_id),
        )
        conn.commit()


def finish_attempt(
    attempt_id: str,
    *,
    status: str,
    failure_type: str | None = None,
    retryable: bool = False,
    exit_code: int | None = None,
    temp_output_image_id: str | None = None,
    output_image_id: str | None = None,
) -> None:
    finished_at = _clock()
    with db.get_connection() as conn:
        conn.execute(
            """
            UPDATE job_attempts
            SET status = ?, finished_at = ?, failure_type = ?, retryable = ?,
                exit_code = ?, temp_output_image_id = COALESCE(?, temp_output_image_id),
                output_image_id = COALESCE(?, output_image_id),
                last_heartbeat_at = ?
            WHERE id = ? AND status = 'running'
            """,
            (
                status,
                finished_at,
                failure_type,
                1 if retryable else 0,
                exit_code,
                temp_output_image_id,
                output_image_id,
                finished_at,
                attempt_id,
            ),
        )
        conn.commit()


def finish_open_attempts(
    job_id: str,
    *,
    status: str,
    failure_type: str | None = None,
    retryable: bool = False,
    message: str | None = None,
    temp_output_image_id: str | None = None,
    output_image_id: str | None = None,
) -> int:
    if message and failure_type is None:
        failure_type, retryable = classify_failure(message)
    with db.get_connection() as conn:
        rows = conn.execute(
            "SELECT id FROM job_attempts WHERE job_id = ? AND status = 'running'",
            (job_id,),
        ).fetchall()
    for row in rows:
        finish_attempt(
            row["id"],
            status=status,
            failure_type=failure_type,
            retryable=retryable,
            temp_output_image_id=temp_output_image_id,
            output_image_id=output_image_id,
            exit_code=1 if status != "succeeded" else 0,
        )
    return len(rows)


def list_attempts(job_id: str) -> list[dict[str, Any]]:
    with db.get_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM job_attempts
            WHERE job_id = ?
            ORDER BY attempt_number ASC
            """,
            (job_id,),
        ).fetchall()
    attempts = []
    for row in rows:
        entry = dict(row)
        entry["retryable"] = bool(entry.get("retryable"))
        attempts.append(entry)
    return attempts


def get_attempt(attempt_id: str) -> dict[str, Any] | None:
    with db.get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM job_attempts WHERE id = ?",
            (attempt_id,),
        ).fetchone()
    if not row:
        return None
    entry = dict(row)
    entry["retryable"] = bool(entry.get("retryable"))
    return entry
