from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any
from typing import Callable


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run one or more edit benchmark review targets through the real upload/job APIs."
    )
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--plan-path", required=True)
    parser.add_argument("--summary-path", required=True)
    parser.add_argument("--model-id", default="qwen-image-edit-2511")
    parser.add_argument("--dotenv-path")
    parser.add_argument("--model-root")
    parser.add_argument("--db-path")
    parser.add_argument("--poll-seconds", type=int, default=5)
    parser.add_argument("--max-wait-seconds", type=int, default=1800)
    return parser.parse_args()


def resolve_path(value: str | None, fallback: Path, *, repo_root: Path) -> Path:
    if not value:
        return fallback
    path = Path(value)
    if not path.is_absolute():
        path = (repo_root / path).resolve()
    return path


def configure_environment(args: argparse.Namespace, repo_root: Path) -> None:
    backend_root = repo_root / "backend"
    os.environ["DOTENV_PATH"] = str(
        resolve_path(args.dotenv_path, backend_root / ".env.fast-check", repo_root=repo_root)
    )
    os.environ["ENABLED_MODELS"] = args.model_id
    os.environ["INFERENCE_MODE"] = "local"
    os.environ["WARMUP_MODELS"] = "0"
    os.environ["MODEL_ROOT"] = str(
        resolve_path(args.model_root, repo_root / "models" / "hf", repo_root=repo_root)
    )
    os.environ["DB_PATH"] = str(
        resolve_path(args.db_path, repo_root / "data" / "app.benchmark-review.db", repo_root=repo_root)
    )


def load_plan(plan_path: Path) -> list[dict[str, Any]]:
    # Accept BOM-marked UTF-8 plans from Windows PowerShell temp-file writes.
    payload = json.loads(plan_path.read_text(encoding="utf-8-sig"))
    targets = payload.get("targets")
    if not isinstance(targets, list) or not targets:
        raise ValueError("Plan file must contain a non-empty 'targets' list.")
    return targets


def write_summary(summary_path: Path, summary: dict[str, Any]) -> None:
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")


def upload_fixture(client: Any, fixture_path: Path) -> str:
    with fixture_path.open("rb") as handle:
        response = client.post(
            "/api/images/upload",
            files={"file": (fixture_path.name, handle, "image/png")},
        )
    response.raise_for_status()
    payload = response.json()
    image_id = payload.get("image_id")
    if not image_id:
        raise RuntimeError(f"Upload did not return an image_id for {fixture_path}.")
    return str(image_id)


def run_target(
    *,
    client: Any,
    jobs_module: Any,
    image_store: Any,
    target: dict[str, Any],
    poll_seconds: int,
    max_wait_seconds: int,
    progress: Callable[[dict[str, Any]], None] | None = None,
) -> dict[str, Any]:
    preset_id = target["preset_id"]
    case_id = target["case_id"]
    base_fixture = Path(target["base_fixture"])
    reference_fixture = Path(target["reference_fixture"]) if target.get("reference_fixture") else None

    if not base_fixture.exists():
        raise FileNotFoundError(f"Base fixture not found: {base_fixture}")
    if reference_fixture and not reference_fixture.exists():
        raise FileNotFoundError(f"Reference fixture not found: {reference_fixture}")

    print(f"[{preset_id}] Uploading fixtures for {case_id}", flush=True)
    image_ids = [upload_fixture(client, base_fixture)]
    if reference_fixture:
        image_ids.append(upload_fixture(client, reference_fixture))
    if progress:
        progress(
            {
                "phase": "uploaded",
                "upload_image_ids": image_ids,
            }
        )

    payload = {
        "model_id": target["model_id"],
        "prompt": target["prompt"],
        "image_ids": image_ids,
        "seed": target["seed"],
        "steps": target["steps"],
    }
    if target.get("guidance_scale") is not None:
        payload["guidance_scale"] = target["guidance_scale"]
    if target.get("true_cfg_scale") is not None:
        payload["true_cfg_scale"] = target["true_cfg_scale"]
    if target.get("strength") is not None:
        payload["strength"] = target["strength"]

    submit_response = client.post("/api/jobs/edit", json=payload)
    submit_response.raise_for_status()
    submit_payload = submit_response.json()
    job_id = submit_payload["job_id"]
    started_at = time.time()
    last_status = None

    print(f"[{preset_id}] Submitted job_id={job_id}", flush=True)
    if progress:
        progress(
            {
                "job_id": job_id,
                "phase": "submitted",
                "status": "queued",
                "elapsed_seconds": 0,
            }
        )

    while True:
        response = client.get(f"/api/jobs/{job_id}")
        response.raise_for_status()
        job = response.json()
        status = job["status"]
        elapsed = int(time.time() - started_at)
        if progress:
            progress(
                {
                    "phase": "polling",
                    "status": status,
                    "elapsed_seconds": elapsed,
                    "error": job.get("error"),
                    "last_polled_at": int(time.time()),
                }
            )
        if status != last_status:
            print(f"[{preset_id}] status={status} elapsed={elapsed}s", flush=True)
            last_status = status

        if status in {"succeeded", "failed", "canceled"}:
            break

        if time.time() - started_at >= max_wait_seconds:
            message = f"benchmark review timeout after {max_wait_seconds}s"
            jobs_module.mark_job_failed(job_id, message)
            response = client.get(f"/api/jobs/{job_id}")
            response.raise_for_status()
            job = response.json()
            status = job["status"]
            break

        time.sleep(poll_seconds)

    run_payload = job.get("run") or {}
    output_image_id = run_payload.get("output_image_id")
    output_path = str(image_store.get_image_path(output_image_id)) if output_image_id else None
    outcome = "blocked" if status == "failed" and (job.get("error") or "").startswith("benchmark review timeout") else status

    return {
        "preset_id": preset_id,
        "case_id": case_id,
        "job_id": job_id,
        "model_id": target["model_id"],
        "upload_image_ids": image_ids,
        "status": status,
        "outcome": outcome,
        "error": job.get("error"),
        "elapsed_seconds": int(time.time() - started_at),
        "output_image_id": output_image_id,
        "output_path": output_path,
    }


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    plan_path = Path(args.plan_path).resolve()
    summary_path = Path(args.summary_path).resolve()
    summary_path.parent.mkdir(parents=True, exist_ok=True)

    summary: dict[str, Any] = {
        "generated_at": int(time.time()),
        "model_id": args.model_id,
        "poll_seconds": args.poll_seconds,
        "max_wait_seconds": args.max_wait_seconds,
        "runner_status": "starting",
        "runner_pid": os.getpid(),
        "results": [],
    }
    write_summary(summary_path, summary)

    configure_environment(args, repo_root)

    try:
        from fastapi.testclient import TestClient
        from app import jobs as jobs_module
        from app.images import get_image_path as _unused_get_image_path  # noqa: F401
        from app import images as image_store
        from app.main import app

        targets = load_plan(plan_path)
        summary["runner_status"] = "running"
        write_summary(summary_path, summary)

        with TestClient(app) as client:
            for target in targets:
                active_result: dict[str, Any] = {
                    "preset_id": target["preset_id"],
                    "case_id": target["case_id"],
                    "model_id": target.get("model_id", args.model_id),
                    "status": "preparing",
                    "outcome": "running",
                }
                summary["results"].append(active_result)
                write_summary(summary_path, summary)

                def progress(update: dict[str, Any]) -> None:
                    active_result.update(update)
                    write_summary(summary_path, summary)

                result = run_target(
                    client=client,
                    jobs_module=jobs_module,
                    image_store=image_store,
                    target={
                        "preset_id": target["preset_id"],
                        "case_id": target["case_id"],
                        "model_id": target.get("model_id", args.model_id),
                        "base_fixture": str(resolve_path(target["base_fixture"], Path(target["base_fixture"]), repo_root=repo_root)),
                        "reference_fixture": str(resolve_path(target["reference_fixture"], Path(target["reference_fixture"]), repo_root=repo_root))
                        if target.get("reference_fixture")
                        else None,
                        "prompt": target["prompt"],
                        "seed": target["seed"],
                        "steps": target["steps"],
                        "guidance_scale": target.get("guidance_scale"),
                        "true_cfg_scale": target.get("true_cfg_scale"),
                        "strength": target.get("strength"),
                    },
                    poll_seconds=args.poll_seconds,
                    max_wait_seconds=args.max_wait_seconds,
                    progress=progress,
                )
                active_result.update(result)
                write_summary(summary_path, summary)
                if result["outcome"] != "succeeded":
                    break
    except Exception as exc:
        summary["runner_status"] = "failed"
        summary["fatal_error"] = str(exc)
        write_summary(summary_path, summary)
        raise

    summary["runner_status"] = "completed"
    write_summary(summary_path, summary)
    print(json.dumps(summary, indent=2), flush=True)

    results = summary["results"]
    if all(result["outcome"] == "succeeded" for result in results):
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
