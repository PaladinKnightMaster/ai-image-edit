"""Hardware scan + model recommendation ("which model fits this machine").

This is the single source of truth behind the `GET /api/hardware` endpoint and the
`scripts/scan_machine.py` CLI. It answers, Ollama-style: given the detected machine,
which image models are recommended, which are usable-but-slow, and which need a GPU
or more resources before they should be downloaded.

Keep the requirement numbers approximate and conservative; they gate large downloads
so users do not pull tens of GB of weights onto a machine that cannot run them.
"""

from __future__ import annotations

import os
import platform
import shutil
from dataclasses import dataclass
from typing import Any

from app import config
from app.model_download import in_app_model_ids

# --- Verdicts ---------------------------------------------------------------

# Ordered best -> worst. Lower rank wins when picking the best choice.
VERDICT_RANK: dict[str, int] = {
    "recommended": 0,
    "usable": 1,
    "usable_slow": 2,
    "needs_more_disk": 3,
    "needs_more_ram": 4,
    "needs_gpu": 5,
}

VERDICT_LABEL: dict[str, str] = {
    "recommended": "Recommended",
    "usable": "Usable",
    "usable_slow": "Usable (slow)",
    "needs_more_disk": "Needs more disk",
    "needs_more_ram": "Needs more RAM",
    "needs_gpu": "Needs a GPU (off-box)",
}


@dataclass(frozen=True)
class ModelReq:
    id: str
    label: str
    engine: str
    capabilities: tuple[str, ...]
    approx_disk_gb: float
    min_ram_gb: float  # system RAM for a tolerable run when running on CPU
    needs_cuda: bool  # a CUDA GPU is required for a usable experience
    min_vram_gb: float | None
    cpu_capable: bool
    cpu_speed: str  # 'fast' | 'slow' | 'very_slow'
    setup: str  # short setup / download hint
    docs: str
    notes: str


# Approximate footprints. Qwen (~20B) is intentionally marked GPU-required because the
# current diffusers path loads fp32 on CPU, which is not runnable on typical machines.
MODEL_REQUIREMENTS: tuple[ModelReq, ...] = (
    ModelReq(
        id="sdxl-openvino",
        label="SDXL 1.0 (OpenVINO, Intel-optimized)",
        engine="openvino",
        capabilities=("t2i", "edit"),
        approx_disk_gb=7.0,
        min_ram_gb=8.0,
        needs_cuda=False,
        min_vram_gb=None,
        cpu_capable=True,
        cpu_speed="fast",
        setup=(
            "hf download OpenVINO/stable-diffusion-xl-base-1.0-int8-ov "
            "--local-dir models/openvino/sdxl_base"
        ),
        docs="docs/models/download-and-setup.md#sdxl-openvino",
        notes=(
            "Best local choice for Intel CPUs/iGPUs: text-to-image and prompt-guided "
            "img2img edit from one OpenVINO INT8 export. Prefer the pre-converted Hub "
            "repo over local export."
        ),
    ),
    ModelReq(
        id="flux2-klein-9b-gguf",
        label="FLUX.2 klein 9B (GGUF)",
        engine="stable-diffusion.cpp",
        capabilities=("t2i", "edit"),
        approx_disk_gb=12.0,
        min_ram_gb=16.0,
        needs_cuda=False,
        min_vram_gb=None,
        cpu_capable=True,
        cpu_speed="very_slow",
        setup="bash scripts/fetch_flux2_klein_gguf.sh  # or the .ps1 on Windows",
        docs="docs/models/download-and-setup.md#flux2-klein-9b-gguf",
        notes=(
            "Runs on CPU but is very slow (~30-40 min/image). Much faster with a GPU "
            "(Vulkan on Intel iGPU, or CUDA)."
        ),
    ),
    ModelReq(
        id="qwen-image-2512",
        label="Qwen-Image 2512 (~20B)",
        engine="diffusers",
        capabilities=("t2i",),
        approx_disk_gb=45.0,
        min_ram_gb=48.0,
        needs_cuda=True,
        min_vram_gb=24.0,
        cpu_capable=False,
        cpu_speed="very_slow",
        setup="python scripts/mirror_models.py --model qwen-image-2512",
        docs="docs/models/download-and-setup.md#qwen-image-family",
        notes=(
            "Frontier text-to-image quality, but requires a CUDA GPU (>=24GB VRAM). "
            "Off-box on CPU-only machines with the current runtime."
        ),
    ),
    ModelReq(
        id="qwen-image-edit-2511",
        label="Qwen-Image-Edit 2511 (~20B)",
        engine="diffusers",
        capabilities=("edit",),
        approx_disk_gb=45.0,
        min_ram_gb=48.0,
        needs_cuda=True,
        min_vram_gb=24.0,
        cpu_capable=False,
        cpu_speed="very_slow",
        setup="python scripts/mirror_models.py --model qwen-image-edit-2511",
        docs="docs/models/download-and-setup.md#qwen-image-family",
        notes=(
            "Primary edit engine at full quality, but requires a CUDA GPU (>=24GB VRAM). "
            "Off-box on CPU-only machines with the current runtime."
        ),
    ),
)

REQ_BY_ID: dict[str, ModelReq] = {req.id: req for req in MODEL_REQUIREMENTS}

# Disk headroom (GB) required on top of a model's footprint before we call it downloadable.
DISK_MARGIN_GB = 3.0


def _cpu_brand() -> str | None:
    try:
        if platform.system() == "Linux" and os.path.exists("/proc/cpuinfo"):
            with open("/proc/cpuinfo", encoding="utf-8", errors="ignore") as handle:
                for line in handle:
                    if line.lower().startswith("model name"):
                        return line.split(":", 1)[1].strip()
        brand = platform.processor()
        return brand or None
    except OSError:
        return None


def _openvino_devices() -> list[str]:
    try:
        import openvino as ov  # type: ignore

        return list(ov.Core().available_devices)
    except Exception:  # noqa: BLE001 - optional dependency / probe, never fatal
        return []


def _disk_free(paths: list) -> tuple[float | None, float | None]:
    for path in paths:
        usage = None
        try:
            usage = shutil.disk_usage(str(path))
        except OSError:
            usage = None
        if usage is not None:
            return (
                round(usage.free / (1024**3), 1),
                round(usage.total / (1024**3), 1),
            )
    return None, None


def detect_hardware() -> dict[str, Any]:
    """Collect a machine profile used for model recommendations."""
    hw: dict[str, Any] = dict(
        config.HARDWARE_INFO
    )  # has_cuda, vram_gb, device_name, ram_gb

    hw["cpu_logical"] = os.cpu_count()
    try:
        import psutil  # type: ignore

        hw["cpu_physical"] = psutil.cpu_count(logical=False)
    except Exception:  # noqa: BLE001 - optional dependency / probe, never fatal
        hw["cpu_physical"] = None

    hw["cpu_brand"] = _cpu_brand()
    hw["os"] = platform.system()
    hw["arch"] = platform.machine()

    probe_dir = config.MODEL_ROOT if config.MODEL_ROOT.exists() else config.REPO_ROOT
    free_gb, total_gb = _disk_free([probe_dir, config.REPO_ROOT])
    hw["disk_free_gb"] = free_gb
    hw["disk_total_gb"] = total_gb

    openvino_devices = _openvino_devices()
    hw["openvino_devices"] = openvino_devices
    hw["has_openvino"] = bool(openvino_devices)
    hw["has_intel_gpu"] = any(dev.startswith("GPU") for dev in openvino_devices)

    return hw


def evaluate_model(req: ModelReq, hw: dict[str, Any]) -> tuple[str, str]:
    """Return (verdict, reason) for one model against the detected hardware."""
    ram = float(hw.get("ram_gb") or 0)
    disk = hw.get("disk_free_gb")
    has_cuda = bool(hw.get("has_cuda"))
    vram = float(hw.get("vram_gb") or 0)

    if req.needs_cuda and not has_cuda:
        return (
            "needs_gpu",
            "Requires a CUDA GPU; not runnable on this CPU-only machine.",
        )
    if req.needs_cuda and has_cuda and req.min_vram_gb and vram < req.min_vram_gb:
        return (
            "needs_gpu",
            f"Requires ~{req.min_vram_gb:.0f}GB VRAM; detected {vram:.1f}GB.",
        )

    if not has_cuda and ram and ram < req.min_ram_gb:
        return (
            "needs_more_ram",
            f"Needs ~{req.min_ram_gb:.0f}GB RAM; detected {ram:.1f}GB.",
        )

    if disk is not None and disk < req.approx_disk_gb + DISK_MARGIN_GB:
        return (
            "needs_more_disk",
            f"Needs ~{req.approx_disk_gb:.0f}GB free (+headroom); detected {disk:.0f}GB free.",
        )

    if has_cuda:
        return "recommended", "Runs well on the detected GPU."
    if req.cpu_speed == "fast":
        return "recommended", "Runs efficiently on this CPU (Intel-optimized path)."
    if req.cpu_speed == "slow":
        return "usable", "Runs on CPU with moderate wait times."
    return (
        "usable_slow",
        "Runs on CPU but is very slow (minutes to tens of minutes per image).",
    )


def _present_map() -> dict[str, bool]:
    try:
        from inference.manager import get_manager

        return {
            entry["id"]: bool(entry["present"]) for entry in get_manager().list_models()
        }
    except Exception:  # noqa: BLE001 - status probe, never fatal for the endpoint
        return {}


def recommend(hw: dict[str, Any] | None = None) -> dict[str, Any]:
    """Full recommendation payload: hardware + per-model verdicts + best choice."""
    hardware = hw or detect_hardware()
    present = _present_map()

    models: list[dict[str, Any]] = []
    for req in MODEL_REQUIREMENTS:
        verdict, reason = evaluate_model(req, hardware)
        models.append(
            {
                "id": req.id,
                "label": req.label,
                "engine": req.engine,
                "capabilities": list(req.capabilities),
                "approx_disk_gb": req.approx_disk_gb,
                "verdict": verdict,
                "verdict_label": VERDICT_LABEL.get(verdict, verdict),
                "reason": reason,
                "downloadable": verdict in {"recommended", "usable", "usable_slow"},
                "in_app_download": req.id in in_app_model_ids(),
                "present": present.get(req.id, False),
                "setup": req.setup,
                "docs": req.docs,
                "notes": req.notes,
            }
        )

    models.sort(
        key=lambda m: (VERDICT_RANK.get(m["verdict"], 99), -m["approx_disk_gb"])
    )

    runnable = [
        m for m in models if m["verdict"] in {"recommended", "usable", "usable_slow"}
    ]
    best = next((m for m in models if m["verdict"] == "recommended"), None)
    if best is None and runnable:
        best = runnable[0]

    best_id = best["id"] if best else None
    if best is None:
        summary = (
            "No bundled model is a clean fit for this machine yet. See the setup guide "
            "for GPU/off-box options."
        )
    else:
        caps = "/".join(best["capabilities"])
        summary = (
            f"Best local pick for this machine: {best['label']} ({caps}). "
            f"{best['reason']}"
        )

    return {
        "hardware": hardware,
        "models": models,
        "best_choice": best_id,
        "best_choice_setup": best["setup"] if best else None,
        "summary": summary,
    }
