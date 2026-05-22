from __future__ import annotations


JOB_STATUS_LABELS = {
    "queued": "Queued",
    "running": "Running locally",
    "pending_review": "Ready for review",
    "succeeded": "Complete",
    "failed": "Failed",
}

JOB_STATUS_DETAILS = {
    "queued": "Waiting for the local backend to start the job.",
    "running": (
        "Local inference is active. CPU runs can take a long time; progress updates when the "
        "backend reports activity."
    ),
    "pending_review": "The output is ready but hidden until it is revealed.",
    "succeeded": "The output is available for compare, download, or reuse.",
    "failed": "The job stopped before producing a reusable output.",
}

STAGE_LABELS = {
    "queued": "Queued",
    "loading": "Loading",
    "running": "Running",
    "saving": "Saving",
    "review": "Review",
    "complete": "Complete",
    "failed": "Failed",
}


def get_job_status_label(status: str | None) -> str:
    if not status:
        return "Waiting"
    return JOB_STATUS_LABELS.get(status, status.replace("_", " ").title())


def get_job_status_detail(status: str | None) -> str:
    if not status:
        return "Waiting for a backend status update."
    return JOB_STATUS_DETAILS.get(status, "Waiting for a backend status update.")


def get_stage_label(stage: str | None) -> str | None:
    if not stage:
        return None
    return STAGE_LABELS.get(stage, stage.replace("_", " "))


def get_failure_detail(error: str | None) -> str | None:
    if error is None:
        return None
    normalized = error.lower()
    if "server restarted" in normalized:
        return (
            "This job was marked failed during backend restart recovery. The run metadata is "
            "safe, but the job is not resumable."
        )
    if "observer_timeout" in normalized:
        return (
            "The observer stopped waiting while the job may still have been active. Treat this "
            "as monitoring evidence, not model-quality failure."
        )
    return error


def with_status_copy(payload: dict) -> dict:
    enriched = dict(payload)
    status = enriched.get("status")
    error = enriched.get("error")
    enriched["status_label"] = get_job_status_label(status)
    enriched["status_detail"] = get_job_status_detail(status)
    if "stage" in enriched:
        enriched["stage_label"] = get_stage_label(enriched.get("stage"))
    if error is not None:
        enriched["error_detail"] = get_failure_detail(error)
    return enriched
