from __future__ import annotations

import sqlite3
from pathlib import Path

from app import config


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    _ensure_parent(config.DB_PATH)
    conn = sqlite3.connect(config.DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_columns(conn: sqlite3.Connection, table: str, columns: list[tuple[str, str]]) -> None:
    existing = {
        row["name"]
        for row in conn.execute(f"PRAGMA table_info({table})").fetchall()
    }
    for name, column_type in columns:
        if name in existing:
            continue
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {column_type}")


def init_db() -> None:
    conn = get_connection()
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                started_at INTEGER,
                finished_at INTEGER,
                error TEXT,
                stage TEXT,
                progress_percent INTEGER,
                progress_step INTEGER,
                progress_total INTEGER,
                last_activity_at INTEGER
            );

            CREATE TABLE IF NOT EXISTS runs (
                id TEXT PRIMARY KEY,
                job_id TEXT NOT NULL,
                model_id TEXT NOT NULL,
                prompt TEXT NOT NULL,
                negative_prompt TEXT,
                seed INTEGER NOT NULL,
                steps INTEGER NOT NULL,
                width INTEGER,
                height INTEGER,
                guidance_scale REAL,
                true_cfg_scale REAL,
                strength REAL,
                input_image_ids TEXT,
                output_image_id TEXT,
                pending_output_image_id TEXT,
                latency_ms INTEGER,
                FOREIGN KEY(job_id) REFERENCES jobs(id)
            );

            CREATE TABLE IF NOT EXISTS images (
                id TEXT PRIMARY KEY,
                filename TEXT,
                source TEXT,
                created_at INTEGER NOT NULL,
                width INTEGER,
                height INTEGER,
                size_bytes INTEGER,
                content_type TEXT,
                job_id TEXT,
                run_id TEXT
            );

            CREATE TABLE IF NOT EXISTS job_attempts (
                id TEXT PRIMARY KEY,
                job_id TEXT NOT NULL,
                attempt_number INTEGER NOT NULL,
                worker_id TEXT,
                execution_mode TEXT,
                status TEXT NOT NULL,
                lease_expires_at INTEGER,
                last_heartbeat_at INTEGER,
                started_at INTEGER NOT NULL,
                finished_at INTEGER,
                exit_code INTEGER,
                failure_type TEXT,
                retryable INTEGER NOT NULL DEFAULT 0,
                temp_output_image_id TEXT,
                output_image_id TEXT,
                FOREIGN KEY(job_id) REFERENCES jobs(id)
            );

            CREATE INDEX IF NOT EXISTS idx_job_attempts_job_id ON job_attempts(job_id);
            """
        )
        _ensure_columns(
            conn,
            "jobs",
            [
                ("stage", "TEXT"),
                ("progress_percent", "INTEGER"),
                ("progress_step", "INTEGER"),
                ("progress_total", "INTEGER"),
                ("last_activity_at", "INTEGER"),
            ],
        )
        _ensure_columns(
            conn,
            "runs",
            [
                ("strength", "REAL"),
                ("pending_output_image_id", "TEXT"),
            ],
        )
        conn.commit()
    finally:
        conn.close()
