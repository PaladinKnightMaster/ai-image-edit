from __future__ import annotations

import abc
import inspect
import logging
import secrets
import threading
from typing import Any, Callable, Iterable

import torch
from PIL import Image
from pydantic import BaseModel, Field, field_validator, model_validator

from app import config

logger = logging.getLogger(__name__)

if not config.OFFLINE_ENABLED:
    logger.warning("Offline mode is disabled; inference may attempt network access.")


def _default_seed() -> int:
    return secrets.randbelow(2**31 - 1)


class GenerationParams(BaseModel):
    prompt: str
    negative_prompt: str | None = None
    seed: int | None = Field(default=None, ge=0)
    steps: int = Field(config.DEFAULT_STEPS, ge=1, le=config.MAX_STEPS)
    width: int = Field(config.DEFAULT_WIDTH, ge=64, le=config.MAX_WIDTH)
    height: int = Field(config.DEFAULT_HEIGHT, ge=64, le=config.MAX_HEIGHT)
    guidance_scale: float | None = Field(default=None, ge=0)
    true_cfg_scale: float | None = Field(default=None, ge=0)

    @field_validator("width", "height")
    @classmethod
    def validate_resolution(cls, value: int) -> int:
        if value % 8 != 0:
            raise ValueError("width and height must be divisible by 8")
        return value

    @model_validator(mode="after")
    def apply_seed(self) -> "GenerationParams":
        if self.seed is None:
            self.seed = _default_seed()
        return self


class EditParams(BaseModel):
    prompt: str
    image_ids: list[str] = Field(min_length=1, max_length=2)
    seed: int | None = Field(default=None, ge=0)
    steps: int = Field(config.DEFAULT_STEPS, ge=1, le=config.MAX_STEPS)
    guidance_scale: float | None = Field(default=None, ge=0)
    true_cfg_scale: float | None = Field(default=None, ge=0)
    strength: float | None = Field(default=None, ge=0, le=1)

    @model_validator(mode="after")
    def apply_seed(self) -> "EditParams":
        if self.seed is None:
            self.seed = _default_seed()
        return self


def _bf16_supported() -> bool:
    checker = getattr(torch.cuda, "is_bf16_supported", None)
    if checker is None:
        return False
    return bool(checker())


def select_device_dtype() -> tuple[str, torch.dtype]:
    if torch.cuda.is_available():
        if _bf16_supported():
            return "cuda", torch.bfloat16
        return "cuda", torch.float16
    logger.warning("CUDA not available. Falling back to CPU inference.")
    return "cpu", torch.float32


def seed_everything(seed: int, device: str) -> torch.Generator:
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    generator = torch.Generator(device=device)
    generator.manual_seed(seed)
    return generator


class Runner(abc.ABC):
    id: str
    label: str = ""
    capabilities: set[str]
    defaults: dict[str, Any] = {}
    manual_review: bool = False

    def __init__(self) -> None:
        self._pipe: Any | None = None
        self._device, self._dtype = select_device_dtype()
        self._lock = threading.Lock()

    @property
    def device(self) -> str:
        return self._device

    @property
    def dtype(self) -> torch.dtype:
        return self._dtype

    def model_status(self) -> dict[str, Any]:
        return {"present": True, "local_path": None, "revision": None}

    def load(self) -> Any:
        if self._pipe is not None:
            return self._pipe
        with self._lock:
            if self._pipe is None:
                logger.info("Loading runner %s with dtype=%s on %s", self.id, self._dtype, self._device)
                self._pipe = self._load_pipeline()
                if hasattr(self._pipe, "to"):
                    self._pipe = self._pipe.to(self._device)
                self._apply_memory_optimizations(self._pipe)
                if hasattr(self._pipe, "set_progress_bar_config"):
                    self._pipe.set_progress_bar_config(disable=True)
        return self._pipe

    @abc.abstractmethod
    def _load_pipeline(self) -> Any:
        raise NotImplementedError

    @abc.abstractmethod
    def generate(
        self,
        params: GenerationParams,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> Image.Image:
        raise NotImplementedError

    @abc.abstractmethod
    def edit(
        self,
        params: EditParams,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> Image.Image:
        raise NotImplementedError

    def _inject_progress_callback(
        self,
        pipe: Any,
        kwargs: dict[str, Any],
        total_steps: int,
        progress_callback: Callable[[int, int], None] | None,
    ) -> dict[str, Any]:
        if progress_callback is None:
            return kwargs

        signature = inspect.signature(pipe.__call__)
        parameters = signature.parameters

        if "callback_on_step_end" in parameters:
            def _callback_on_step_end(
                _pipe: Any, step: int, _timestep: Any, callback_kwargs: dict[str, Any]
            ) -> dict[str, Any]:
                progress_callback(step + 1, total_steps)
                return callback_kwargs

            kwargs["callback_on_step_end"] = _callback_on_step_end
            return kwargs

        if "callback" in parameters and "callback_steps" in parameters:
            def _callback(step: int, _timestep: Any, _latents: Any) -> None:
                progress_callback(step + 1, total_steps)

            kwargs["callback"] = _callback
            kwargs["callback_steps"] = 1
            return kwargs

        return kwargs

    def _apply_memory_optimizations(self, pipe: Any) -> None:
        if config.ENABLE_ATTENTION_SLICING and hasattr(pipe, "enable_attention_slicing"):
            pipe.enable_attention_slicing()
        if config.ENABLE_VAE_SLICING and hasattr(pipe, "enable_vae_slicing"):
            pipe.enable_vae_slicing()
        if config.ENABLE_VAE_TILING and hasattr(pipe, "enable_vae_tiling"):
            pipe.enable_vae_tiling()
