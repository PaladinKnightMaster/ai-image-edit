from __future__ import annotations

from contextlib import asynccontextmanager
import io
import json
import math
import threading
import sys
import time
import urllib.error
import urllib.request
from typing import List

from fastapi import FastAPI, UploadFile, File, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, ValidationError
from PIL import Image

from app import config, images as image_store, jobs, ready, logging_utils, model_registry, storage
from app import hardware as hardware_advisor
from app.errors import APIError, register_error_handlers
from inference.base import EditParams, GenerationParams
from inference.manager import get_manager
from inference.flux2_klein_gguf import flux2_diagnostics

APP_NAME = config.APP_NAME
APP_VERSION = config.APP_VERSION
APP_COMMIT = config.APP_COMMIT
FRONTEND_ORIGIN = config.FRONTEND_ORIGIN

logging_utils.setup_logging()

def parse_origins(value: str) -> List[str]:
    return [origin.strip() for origin in value.split(",") if origin.strip()]


@asynccontextmanager
async def lifespan(_: FastAPI):
    jobs.init_jobs()
    ready.set_state(False, "starting", {"message": "server starting"})
    if config.INFERENCE_MODE == "worker":
        ready.set_state(True, "worker", {"message": "inference handled by worker"})
        yield
        return
    if config.WARMUP_MODELS:
        ready.set_state(False, "warming", {"message": "warming models"})

        def _warmup() -> None:
            try:
                logging_utils.log_event("warmup_start")
                get_manager().warmup_all()
                ready.set_state(True, "ready", {"message": "models warmed"})
                logging_utils.log_event("warmup_success")
            except Exception as exc:
                error_message = f"{exc.__class__.__name__}: {exc}"
                ready.set_state(False, "degraded", {"error": error_message})
                logging_utils.log_exception("warmup_failed", exc)

        thread = threading.Thread(target=_warmup, daemon=True)
        thread.start()
        thread.join(timeout=config.WARMUP_TIMEOUT_SEC)
        if thread.is_alive():
            ready.set_state(
                False,
                "degraded",
                {"error": "warmup timeout", "timeout_sec": config.WARMUP_TIMEOUT_SEC},
            )
            logging_utils.log_error(
                "warmup_timeout", timeout_sec=config.WARMUP_TIMEOUT_SEC
            )
    else:
        ready.set_state(True, "skipped", {"message": "warmup disabled"})
    yield


app = FastAPI(title=APP_NAME, version=APP_VERSION, lifespan=lifespan)
register_error_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=parse_origins(FRONTEND_ORIGIN),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class HealthResponse(BaseModel):
    status: str


class VersionResponse(BaseModel):
    name: str
    version: str
    commit: str


class ModelStatus(BaseModel):
    id: str
    label: str
    capabilities: list[str]
    edit_input_limit: int | None = None
    present: bool
    local_path: str | None = None
    revision: str | None = None
    detail: str | None = None
    defaults: dict | None = None
    review_mode: str | None = None


class T2IRequest(GenerationParams):
    model_id: str


class EditRequest(EditParams):
    model_id: str


class InferResponse(BaseModel):
    image_id: str


class JobSubmitResponse(BaseModel):
    job_id: str


class UploadResponse(BaseModel):
    image_id: str


class RunResponse(BaseModel):
    id: str
    job_id: str
    model_id: str
    prompt: str
    negative_prompt: str | None = None
    seed: int
    steps: int
    width: int | None = None
    height: int | None = None
    guidance_scale: float | None = None
    true_cfg_scale: float | None = None
    strength: float | None = None
    input_image_ids: list[str] | None = None
    output_image_id: str | None = None
    pending_output_image_id: str | None = None
    latency_ms: int | None = None
    type: str | None = None
    status: str | None = None
    status_label: str | None = None
    status_detail: str | None = None
    error: str | None = None
    error_detail: str | None = None
    created_at: int | None = None
    finished_at: int | None = None


class JobResponse(BaseModel):
    id: str
    type: str
    status: str
    status_label: str | None = None
    status_detail: str | None = None
    created_at: int
    started_at: int | None = None
    finished_at: int | None = None
    error: str | None = None
    error_detail: str | None = None
    stage: str | None = None
    stage_label: str | None = None
    progress_percent: int | None = None
    progress_step: int | None = None
    progress_total: int | None = None
    last_activity_at: int | None = None
    run: RunResponse | None = None


class SystemResponse(BaseModel):
    profile: str
    profile_reason: str
    hardware: dict
    defaults: dict
    limits: dict
    memory: dict
    storage: dict | None = None


class HardwareRecommendation(BaseModel):
    id: str
    label: str
    engine: str
    capabilities: list[str]
    approx_disk_gb: float
    verdict: str
    verdict_label: str
    reason: str
    downloadable: bool
    present: bool
    setup: str
    docs: str
    notes: str


class HardwareResponse(BaseModel):
    hardware: dict
    models: list[HardwareRecommendation]
    best_choice: str | None = None
    best_choice_setup: str | None = None
    summary: str


class ReadyResponse(BaseModel):
    ready: bool
    status: str
    details: dict


class StatsResponse(BaseModel):
    queue_length: int
    current_running_job_id: str | None = None
    latency_ms: dict
    gpu: dict


class ReplayRequest(BaseModel):
    run_id: str | None = None
    export: dict | None = None


class RevealResponse(BaseModel):
    image_id: str


class DeleteRunsResponse(BaseModel):
    deleted: int


class JobEventRequest(BaseModel):
    event: str
    data: dict


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/ready", response_model=ReadyResponse)
def ready_check() -> ReadyResponse:
    if config.INFERENCE_MODE == "worker":
        url = config.WORKER_URL.rstrip("/") + "/health"
        try:
            with urllib.request.urlopen(url, timeout=config.WORKER_HEALTH_TIMEOUT_SEC) as response:
                payload = {}
                if response.status >= 400:
                    raise RuntimeError(f"Worker returned status {response.status}.")
                raw = response.read().decode("utf-8").strip()
                if raw:
                    payload = json.loads(raw)
            return ReadyResponse(
                ready=True,
                status="worker_ready",
                details={"worker_url": config.WORKER_URL, "worker_status": payload.get("status")},
            )
        except Exception as exc:
            return ReadyResponse(
                ready=False,
                status="worker_unavailable",
                details={"worker_url": config.WORKER_URL, "error": str(exc)},
            )
    state = ready.get_state()
    return ReadyResponse(ready=state["ready"], status=state["status"], details=state["details"])


@app.get("/api/version", response_model=VersionResponse)
def version() -> VersionResponse:
    return VersionResponse(name=APP_NAME, version=APP_VERSION, commit=APP_COMMIT)


@app.get("/api/models", response_model=list[ModelStatus])
def list_models() -> list[ModelStatus]:
    return get_manager().list_models()


@app.get("/api/system", response_model=SystemResponse)
def get_system() -> SystemResponse:
    system = dict(config.SYSTEM_INFO)
    system["storage"] = storage.get_storage_info()
    return system


@app.get("/api/hardware", response_model=HardwareResponse)
def get_hardware() -> HardwareResponse:
    return hardware_advisor.recommend()


@app.post("/api/jobs/t2i", response_model=JobSubmitResponse)
def submit_t2i_job(request: T2IRequest) -> JobSubmitResponse:
    params = GenerationParams.model_validate(request.model_dump(exclude={"model_id"}))
    try:
        job_id = jobs.submit_job("t2i", request.model_id, params)
    except ValueError as exc:
        raise APIError("invalid_request", str(exc), status_code=400) from exc
    return JobSubmitResponse(job_id=job_id)


@app.post("/api/images/generate", response_model=JobSubmitResponse)
def generate_image(request: T2IRequest) -> JobSubmitResponse:
    return submit_t2i_job(request)


@app.post("/api/jobs/edit", response_model=JobSubmitResponse)
def submit_edit_job(request: EditRequest) -> JobSubmitResponse:
    params = EditParams.model_validate(request.model_dump(exclude={"model_id"}))
    try:
        job_id = jobs.submit_job("edit", request.model_id, params)
    except ValueError as exc:
        raise APIError("invalid_request", str(exc), status_code=400) from exc
    return JobSubmitResponse(job_id=job_id)


@app.post("/api/images/edit", response_model=JobSubmitResponse)
def edit_image(request: EditRequest) -> JobSubmitResponse:
    return submit_edit_job(request)


@app.get("/api/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: str) -> JobResponse:
    job = jobs.get_job(job_id)
    if not job:
        raise APIError("not_found", "Job not found.", status_code=404)
    return job


@app.post("/api/jobs/{job_id}/reveal", response_model=RevealResponse)
def reveal_job(job_id: str) -> RevealResponse:
    try:
        image_id = jobs.reveal_job(job_id)
    except ValueError as exc:
        raise APIError("invalid_request", str(exc), status_code=400) from exc
    return RevealResponse(image_id=image_id)


@app.get("/api/jobs/{job_id}/events")
def stream_job_events(job_id: str, request: Request) -> StreamingResponse:
    job = jobs.get_job(job_id)
    if not job:
        raise APIError("not_found", "Job not found.", status_code=404)
    return StreamingResponse(
        jobs.stream_events(job_id, request),
        media_type="text/event-stream",
    )


@app.post("/api/internal/jobs/{job_id}/event")
def publish_job_event(
    job_id: str,
    payload: JobEventRequest,
    authorization: str | None = Header(default=None),
) -> dict:
    if config.WORKER_TOKEN:
        expected = f"Bearer {config.WORKER_TOKEN}"
        if authorization != expected:
            raise APIError("unauthorized", "Invalid worker token.", status_code=401)
    jobs.publish_event(job_id, payload.event, payload.data)
    return {"ok": True}


@app.get("/api/runs", response_model=list[RunResponse])
def list_runs(limit: int = 50, status: str | None = None) -> list[RunResponse]:
    return jobs.list_runs(limit=limit, status=status)


@app.delete("/api/runs/{run_id}", response_model=DeleteRunsResponse)
def delete_run(run_id: str, delete_images: bool = False) -> DeleteRunsResponse:
    run = jobs.get_run(run_id)
    if not run:
        raise APIError("not_found", "Run not found.", status_code=404)
    if run.get("status") in {"queued", "running"}:
        raise APIError(
            "invalid_request",
            "Cannot delete a queued or running run.",
            status_code=409,
        )
    if not jobs.delete_run(run_id, delete_images=delete_images):
        raise APIError("not_found", "Run not found.", status_code=404)
    return DeleteRunsResponse(deleted=1)


@app.delete("/api/runs", response_model=DeleteRunsResponse)
def delete_runs(
    status: str | None = None,
    limit: int | None = None,
    delete_images: bool = False,
) -> DeleteRunsResponse:
    try:
        deleted = jobs.delete_runs(status=status, limit=limit, delete_images=delete_images)
    except ValueError as exc:
        raise APIError("invalid_request", str(exc), status_code=400) from exc
    return DeleteRunsResponse(deleted=deleted)


@app.get("/api/diagnostics/engines")
def engine_diagnostics() -> dict:
    return {"flux2_klein_gguf": flux2_diagnostics()}


@app.post("/api/infer/t2i", response_model=InferResponse)
def infer_t2i(request: T2IRequest) -> InferResponse:
    manager = get_manager()
    try:
        runner = manager.get_runner(request.model_id)
    except KeyError as exc:
        raise APIError("not_found", str(exc), status_code=404) from exc
    if "t2i" not in runner.capabilities:
        raise APIError(
            "invalid_request",
            "Model does not support text-to-image.",
            status_code=400,
        )

    params = GenerationParams.model_validate(request.model_dump(exclude={"model_id"}))
    try:
        image = runner.generate(params)
    except (FileNotFoundError, ValueError) as exc:
        raise APIError("invalid_request", str(exc), status_code=400) from exc
    image_id, _ = image_store.save_image(image, source="infer")
    return InferResponse(image_id=image_id)


@app.post("/api/infer/edit", response_model=InferResponse)
def infer_edit(request: EditRequest) -> InferResponse:
    manager = get_manager()
    try:
        runner = manager.get_runner(request.model_id)
    except KeyError as exc:
        raise APIError("not_found", str(exc), status_code=404) from exc
    if "edit" not in runner.capabilities:
        raise APIError("invalid_request", "Model does not support image editing.", status_code=400)

    params = EditParams.model_validate(request.model_dump(exclude={"model_id"}))
    try:
        image = runner.edit(params)
    except (FileNotFoundError, ValueError) as exc:
        raise APIError("invalid_request", str(exc), status_code=400) from exc
    image_id, _ = image_store.save_image(image, source="infer")
    return InferResponse(image_id=image_id)


@app.post("/api/images/upload", response_model=UploadResponse)
async def upload_images(file: UploadFile = File(...)) -> UploadResponse:
    if not file:
        raise APIError("invalid_upload", "No file uploaded.", status_code=400)

    allowed_types = {"image/png", "image/jpeg", "image/webp"}
    if file.content_type not in allowed_types:
        raise APIError("invalid_upload", "Unsupported image type.", status_code=400)

    try:
        content = await file.read()
        if len(content) > config.MAX_UPLOAD_BYTES:
            raise APIError(
                "invalid_upload",
                f"File too large. Max {config.MAX_UPLOAD_MB} MB.",
                status_code=400,
            )
        image = Image.open(io.BytesIO(content))
        image.load()
    except APIError:
        raise
    except Exception as exc:
        raise APIError("invalid_upload", "Invalid image file.", status_code=400) from exc
    finally:
        await file.close()

    image_id, _ = image_store.save_image(
        image,
        filename=file.filename,
        source="upload",
        content_type=file.content_type,
        size_bytes=len(content),
    )
    return UploadResponse(image_id=image_id)


@app.get("/api/images/{image_id}")
def get_image(image_id: str) -> FileResponse:
    path = image_store.get_image_path(image_id)
    if not path.exists():
        raise APIError("not_found", "Image not found.", status_code=404)
    return FileResponse(path, media_type="image/png")


@app.get("/api/images/{image_id}/meta")
def get_image_meta(image_id: str) -> dict:
    meta = image_store.get_image_metadata(image_id)
    if not meta:
        raise APIError("not_found", "Image metadata not found.", status_code=404)
    return meta


@app.get("/api/stats", response_model=StatsResponse)
def get_stats() -> StatsResponse:
    latencies = jobs.get_recent_latencies(50)
    latencies_sorted = sorted(latencies)

    def percentile(values: list[int], pct: float) -> int | None:
        if not values:
            return None
        index = int(math.ceil((pct / 100) * len(values))) - 1
        index = max(0, min(index, len(values) - 1))
        return values[index]

    gpu_info: dict = {"available": False}
    try:
        import torch  # type: ignore

        if torch.cuda.is_available():
            props = torch.cuda.get_device_properties(0)
            gpu_info = {
                "available": True,
                "name": props.name,
                "total_memory_gb": round(props.total_memory / (1024**3), 1),
            }
    except Exception:
        pass

    return StatsResponse(
        queue_length=jobs.get_queue_length(),
        current_running_job_id=jobs.get_current_job_id(),
        latency_ms={
            "count": len(latencies_sorted),
            "p50": percentile(latencies_sorted, 50),
            "p95": percentile(latencies_sorted, 95),
        },
        gpu=gpu_info,
    )


@app.get("/api/runs/{run_id}/export")
def export_run(run_id: str) -> dict:
    run = jobs.get_run(run_id)
    if not run:
        raise APIError("not_found", "Run not found.", status_code=404)

    model_path = None
    try:
        model_path = str(model_registry.resolve_model_path(run["model_id"]))
    except Exception:
        model_path = None

    versions = {"python": sys.version.split()[0]}
    try:
        import torch  # type: ignore

        versions["torch"] = torch.__version__
    except Exception:
        versions["torch"] = None
    try:
        import diffusers  # type: ignore

        versions["diffusers"] = diffusers.__version__
    except Exception:
        versions["diffusers"] = None

    export = {
        "run_id": run["id"],
        "job_id": run["job_id"],
        "type": run.get("type"),
        "model_id": run["model_id"],
        "model_path": model_path,
        "model_revision": config.MODEL_REVISION,
        "prompt": run["prompt"],
        "negative_prompt": run.get("negative_prompt"),
        "seed": run["seed"],
        "steps": run["steps"],
        "width": run.get("width"),
        "height": run.get("height"),
        "guidance_scale": run.get("guidance_scale"),
        "true_cfg_scale": run.get("true_cfg_scale"),
        "strength": run.get("strength"),
        "input_image_ids": run.get("input_image_ids"),
        "output_image_id": run.get("output_image_id"),
        "created_at": run.get("created_at"),
        "software": versions,
        "exported_at": int(time.time() * 1000),
    }
    return export


@app.post("/api/jobs/replay", response_model=JobSubmitResponse)
def replay_job(request: ReplayRequest) -> JobSubmitResponse:
    if bool(request.run_id) == bool(request.export):
        raise APIError(
            "invalid_request",
            "Provide either run_id or export payload.",
            status_code=400,
        )

    if request.run_id:
        run = jobs.get_run(request.run_id)
        if not run:
            raise APIError("not_found", "Run not found.", status_code=404)
        payload = run
    else:
        payload = request.export or {}

    model_id = payload.get("model_id")
    job_type = payload.get("type")
    if not model_id or not job_type:
        raise APIError(
            "invalid_request",
            "Replay payload missing model_id or type.",
            status_code=400,
        )

    if job_type == "t2i":
        try:
            params = GenerationParams(
                prompt=payload.get("prompt", ""),
                negative_prompt=payload.get("negative_prompt"),
                seed=payload.get("seed"),
                steps=payload.get("steps", config.DEFAULT_STEPS),
                width=payload.get("width", config.DEFAULT_WIDTH),
                height=payload.get("height", config.DEFAULT_HEIGHT),
                guidance_scale=payload.get("guidance_scale"),
                true_cfg_scale=payload.get("true_cfg_scale"),
            )
            job_id = jobs.submit_job("t2i", model_id, params)
        except ValidationError as exc:
            raise APIError(
                "invalid_request",
                "Replay payload invalid.",
                status_code=400,
                details=exc.errors(),
            ) from exc
        except ValueError as exc:
            raise APIError("invalid_request", str(exc), status_code=400) from exc
    elif job_type == "edit":
        try:
            params = EditParams(
                prompt=payload.get("prompt", ""),
                image_ids=payload.get("input_image_ids") or [],
                seed=payload.get("seed"),
                steps=payload.get("steps", config.DEFAULT_STEPS),
                guidance_scale=payload.get("guidance_scale"),
                true_cfg_scale=payload.get("true_cfg_scale"),
                strength=payload.get("strength"),
            )
            job_id = jobs.submit_job("edit", model_id, params)
        except ValidationError as exc:
            raise APIError(
                "invalid_request",
                "Replay payload invalid.",
                status_code=400,
                details=exc.errors(),
            ) from exc
        except ValueError as exc:
            raise APIError("invalid_request", str(exc), status_code=400) from exc
    else:
        raise APIError("invalid_request", "Unknown run type.", status_code=400)

    return JobSubmitResponse(job_id=job_id)
