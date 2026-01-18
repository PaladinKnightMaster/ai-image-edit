from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]

APP_NAME = os.getenv("APP_NAME", "ai-image-edit")
APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
APP_COMMIT = os.getenv("APP_COMMIT", "dev")
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
DEBUG = os.getenv("DEBUG", "0").lower() not in {"0", "false", "no"}


def _resolve_path(value: str | Path, base: Path) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = (base / path).resolve()
    return path


MODEL_ROOT = _resolve_path(os.getenv("MODEL_ROOT", REPO_ROOT / "models" / "hf"), REPO_ROOT)
MODEL_REVISION = os.getenv("MODEL_REVISION")

DB_PATH = _resolve_path(os.getenv("DB_PATH", REPO_ROOT / "data" / "app.db"), REPO_ROOT)

MAX_CONCURRENT_JOBS = int(os.getenv("MAX_CONCURRENT_JOBS", "1"))
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "10"))
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024
WARMUP_MODELS = os.getenv("WARMUP_MODELS", "1").lower() not in {"0", "false", "no"}
WARMUP_TIMEOUT_SEC = int(os.getenv("WARMUP_TIMEOUT_SEC", "300"))

QUALITY_PROFILE = os.getenv("QUALITY_PROFILE", "auto").lower()


def _env_int(name: str) -> int | None:
    if name not in os.environ:
        return None
    return int(os.environ[name])


def _env_flag(name: str) -> bool | None:
    if name not in os.environ:
        return None
    return os.environ[name].lower() not in {"0", "false", "no"}


@dataclass(frozen=True)
class ProfileSettings:
    name: str
    default_width: int
    default_height: int
    default_steps: int
    max_width: int
    max_height: int
    max_steps: int
    attention_slicing: bool
    vae_slicing: bool
    vae_tiling: bool


PROFILES: dict[str, ProfileSettings] = {
    "cpu-low": ProfileSettings(
        name="cpu-low",
        default_width=512,
        default_height=512,
        default_steps=12,
        max_width=640,
        max_height=640,
        max_steps=20,
        attention_slicing=True,
        vae_slicing=True,
        vae_tiling=True,
    ),
    "cpu-balanced": ProfileSettings(
        name="cpu-balanced",
        default_width=640,
        default_height=640,
        default_steps=16,
        max_width=768,
        max_height=768,
        max_steps=24,
        attention_slicing=True,
        vae_slicing=True,
        vae_tiling=True,
    ),
    "low": ProfileSettings(
        name="low",
        default_width=768,
        default_height=768,
        default_steps=20,
        max_width=1024,
        max_height=1024,
        max_steps=30,
        attention_slicing=True,
        vae_slicing=True,
        vae_tiling=False,
    ),
    "balanced": ProfileSettings(
        name="balanced",
        default_width=1024,
        default_height=1024,
        default_steps=24,
        max_width=1280,
        max_height=1280,
        max_steps=35,
        attention_slicing=True,
        vae_slicing=True,
        vae_tiling=False,
    ),
    "high": ProfileSettings(
        name="high",
        default_width=1024,
        default_height=1024,
        default_steps=28,
        max_width=1536,
        max_height=1536,
        max_steps=40,
        attention_slicing=False,
        vae_slicing=False,
        vae_tiling=False,
    ),
    "ultra": ProfileSettings(
        name="ultra",
        default_width=1024,
        default_height=1024,
        default_steps=40,
        max_width=2048,
        max_height=2048,
        max_steps=60,
        attention_slicing=False,
        vae_slicing=False,
        vae_tiling=False,
    ),
}


def _detect_hardware() -> dict[str, float | str | bool | None]:
    info: dict[str, float | str | bool | None] = {
        "has_cuda": False,
        "vram_gb": None,
        "device_name": None,
        "ram_gb": None,
    }
    try:
        import psutil  # type: ignore

        info["ram_gb"] = round(psutil.virtual_memory().total / (1024**3), 1)
    except Exception:
        pass

    try:
        import torch  # type: ignore

        if torch.cuda.is_available():
            props = torch.cuda.get_device_properties(0)
            info["has_cuda"] = True
            info["device_name"] = props.name
            info["vram_gb"] = round(props.total_memory / (1024**3), 1)
    except Exception:
        pass

    return info


def _select_profile(profile_name: str, hardware: dict[str, float | str | bool | None]) -> tuple[ProfileSettings, str]:
    if profile_name != "auto":
        preset = PROFILES.get(profile_name)
        if not preset:
            raise ValueError(f"Unknown QUALITY_PROFILE '{profile_name}'.")
        return preset, "manual"

    if hardware.get("has_cuda"):
        vram = float(hardware.get("vram_gb") or 0)
        if vram >= 24:
            return PROFILES["ultra"], f"auto cuda vram {vram}GB"
        if vram >= 16:
            return PROFILES["high"], f"auto cuda vram {vram}GB"
        if vram >= 12:
            return PROFILES["balanced"], f"auto cuda vram {vram}GB"
        if vram >= 8:
            return PROFILES["low"], f"auto cuda vram {vram}GB"
        return PROFILES["low"], f"auto cuda vram {vram}GB"

    ram = float(hardware.get("ram_gb") or 0)
    if ram >= 32:
        return PROFILES["cpu-balanced"], f"auto cpu ram {ram}GB"
    return PROFILES["cpu-low"], f"auto cpu ram {ram}GB"


HARDWARE_INFO = _detect_hardware()
_profile = _select_profile(QUALITY_PROFILE, HARDWARE_INFO)
_profile_settings, PROFILE_REASON = _profile
EFFECTIVE_PROFILE = _profile_settings.name

DEFAULT_WIDTH = _env_int("DEFAULT_WIDTH") or _profile_settings.default_width
DEFAULT_HEIGHT = _env_int("DEFAULT_HEIGHT") or _profile_settings.default_height
DEFAULT_STEPS = _env_int("DEFAULT_STEPS") or _profile_settings.default_steps

MAX_WIDTH = _env_int("MAX_WIDTH") or min(_profile_settings.max_width, 1024)
MAX_HEIGHT = _env_int("MAX_HEIGHT") or min(_profile_settings.max_height, 1024)
MAX_STEPS = _env_int("MAX_STEPS") or min(_profile_settings.max_steps, 50)

if DEFAULT_WIDTH > MAX_WIDTH:
    DEFAULT_WIDTH = MAX_WIDTH
if DEFAULT_HEIGHT > MAX_HEIGHT:
    DEFAULT_HEIGHT = MAX_HEIGHT
if DEFAULT_STEPS > MAX_STEPS:
    DEFAULT_STEPS = MAX_STEPS

ENABLE_ATTENTION_SLICING = _env_flag("ENABLE_ATTENTION_SLICING")
ENABLE_VAE_SLICING = _env_flag("ENABLE_VAE_SLICING")
ENABLE_VAE_TILING = _env_flag("ENABLE_VAE_TILING")

if ENABLE_ATTENTION_SLICING is None:
    ENABLE_ATTENTION_SLICING = _profile_settings.attention_slicing
if ENABLE_VAE_SLICING is None:
    ENABLE_VAE_SLICING = _profile_settings.vae_slicing
if ENABLE_VAE_TILING is None:
    ENABLE_VAE_TILING = _profile_settings.vae_tiling

SYSTEM_INFO = {
    "profile": EFFECTIVE_PROFILE,
    "profile_reason": PROFILE_REASON,
    "hardware": HARDWARE_INFO,
    "defaults": {
        "width": DEFAULT_WIDTH,
        "height": DEFAULT_HEIGHT,
        "steps": DEFAULT_STEPS,
    },
    "limits": {
        "max_width": MAX_WIDTH,
        "max_height": MAX_HEIGHT,
        "max_steps": MAX_STEPS,
        "max_upload_mb": MAX_UPLOAD_MB,
    },
    "memory": {
        "attention_slicing": ENABLE_ATTENTION_SLICING,
        "vae_slicing": ENABLE_VAE_SLICING,
        "vae_tiling": ENABLE_VAE_TILING,
    },
}

OFFLINE_MODE = os.getenv("OFFLINE_MODE", "1")
OFFLINE_ENABLED = OFFLINE_MODE.lower() not in {"0", "false", "no"}

CACHE_ROOT = _resolve_path(
    os.getenv("HF_CACHE_ROOT", REPO_ROOT / "models" / "cache"), REPO_ROOT
)
HF_HOME = _resolve_path(os.getenv("HF_HOME", CACHE_ROOT / "hf_home"), REPO_ROOT)
HF_HUB_CACHE = _resolve_path(
    os.getenv("HF_HUB_CACHE", CACHE_ROOT / "hf_hub"), REPO_ROOT
)
TRANSFORMERS_CACHE = _resolve_path(
    os.getenv("TRANSFORMERS_CACHE", CACHE_ROOT / "transformers"), REPO_ROOT
)


def _ensure_dirs(paths: Iterable[Path]) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def configure_hf_environment() -> None:
    _ensure_dirs([MODEL_ROOT, CACHE_ROOT, HF_HOME, HF_HUB_CACHE, TRANSFORMERS_CACHE])
    os.environ.setdefault("HF_HOME", str(HF_HOME))
    os.environ.setdefault("HF_HUB_CACHE", str(HF_HUB_CACHE))
    os.environ.setdefault("TRANSFORMERS_CACHE", str(TRANSFORMERS_CACHE))
    os.environ.setdefault("DIFFUSERS_DISABLE_PROGRESS_BAR", "1")
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
    if OFFLINE_ENABLED:
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"


configure_hf_environment()
