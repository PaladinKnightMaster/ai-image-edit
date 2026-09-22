from __future__ import annotations

import inspect
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from PIL import Image

from app import config, images as image_store
from inference.base import EditParams, GenerationParams, Runner, seed_everything

# Default edit strength when the client leaves it unset. High enough to apply the
# prompt, low enough to keep the source portrait's identity.
DEFAULT_EDIT_STRENGTH = 0.65


@dataclass
class _SDXLOVPipelines:
    base: Any
    refiner: Any | None
    img2img: Any | None = None


def _filter_kwargs(callable_obj: Any, kwargs: dict[str, Any]) -> dict[str, Any]:
    try:
        signature = inspect.signature(callable_obj)
    except (TypeError, ValueError):
        return kwargs
    parameters = signature.parameters.values()
    # Optimum Intel wraps its pipelines as `__call__(self, *args, **kwargs)`, so the
    # real parameters are not introspectable. Filtering against that signature would
    # drop everything (including `prompt`), so forward kwargs untouched instead.
    if any(param.kind is inspect.Parameter.VAR_KEYWORD for param in parameters):
        return kwargs
    valid = {param.name for param in parameters}
    return {key: value for key, value in kwargs.items() if key in valid}


def _ensure_dir(path: Path, label: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"{label} OpenVINO model not found at {path}.")


def _normalize_image(result: Any) -> Image.Image:
    if isinstance(result, Image.Image):
        return result
    if isinstance(result, (list, tuple)) and result:
        return _normalize_image(result[0])
    if hasattr(result, "images"):
        images = getattr(result, "images")
        if images:
            return _normalize_image(images[0])
    if hasattr(result, "shape"):
        return Image.fromarray(result)
    raise RuntimeError("Unexpected output from SDXL OpenVINO pipeline.")


def _extract_latents(result: Any) -> Any:
    if hasattr(result, "images"):
        images = getattr(result, "images")
        if images is not None:
            return images
    if hasattr(result, "latents"):
        return getattr(result, "latents")
    if isinstance(result, (list, tuple)) and result:
        return result[0]
    return result


def _fit_image(image: Image.Image, max_width: int, max_height: int) -> Image.Image:
    """Resize to fit within limits while keeping aspect ratio and 8-pixel alignment."""
    rgb = image.convert("RGB")
    width, height = rgb.size
    scale = min(max_width / max(width, 1), max_height / max(height, 1), 1.0)
    target_w = max(8, int(round(width * scale / 8.0)) * 8)
    target_h = max(8, int(round(height * scale / 8.0)) * 8)
    target_w = min(target_w, max_width - (max_width % 8))
    target_h = min(target_h, max_height - (max_height % 8))
    if (target_w, target_h) == rgb.size:
        return rgb
    return rgb.resize((target_w, target_h), Image.Resampling.LANCZOS)


def _load_ov_pipeline(pipeline_cls: Any, model_dir: Path) -> Any:
    kwargs = {
        "device": config.SDXL_OV_DEVICE,
        "compile": config.SDXL_OV_COMPILE,
    }
    kwargs = _filter_kwargs(pipeline_cls.from_pretrained, kwargs)
    pipe = pipeline_cls.from_pretrained(str(model_dir), **kwargs)
    if hasattr(pipe, "to"):
        pipe = pipe.to(config.SDXL_OV_DEVICE)
    return pipe


class SDXLOpenVINORunner(Runner):
    id = "sdxl-openvino"
    label = "SDXL 1.0 (OpenVINO)"
    capabilities = {"t2i", "edit"}
    edit_input_limit = 1
    defaults = {
        "steps": config.DEFAULT_STEPS,
        "width": config.DEFAULT_WIDTH,
        "height": config.DEFAULT_HEIGHT,
        "strength": DEFAULT_EDIT_STRENGTH,
    }

    def __init__(self) -> None:
        super().__init__()
        self._backend_name = "openvino"
        self._device = f"openvino:{config.SDXL_OV_DEVICE}"

    @property
    def backend_name(self) -> str:
        return self._backend_name

    def model_status(self) -> dict[str, Any]:
        base_dir = config.SDXL_OV_BASE_DIR
        refiner_dir = config.SDXL_OV_REFINER_DIR
        base_present = base_dir.exists()
        refiner_present = refiner_dir.exists()
        if config.SDXL_REFINER_ENABLED:
            present = base_present and refiner_present
            detail = None
            if not base_present:
                detail = "SDXL base missing."
            elif not refiner_present:
                detail = "SDXL refiner missing."
        else:
            present = base_present
            detail = None if base_present else "SDXL base missing."
        return {
            "present": present,
            "local_path": str(base_dir),
            "revision": None,
            "detail": detail,
        }

    def _load_pipeline(self) -> _SDXLOVPipelines:
        try:
            from optimum.intel.openvino import OVStableDiffusionXLPipeline
        except Exception as exc:  # pragma: no cover - optional dependency
            raise ImportError(
                "OpenVINO SDXL requires optimum-intel with OpenVINO runtime installed."
            ) from exc

        base_dir = config.SDXL_OV_BASE_DIR
        _ensure_dir(base_dir, "SDXL base")

        base = _load_ov_pipeline(OVStableDiffusionXLPipeline, base_dir)
        self._apply_memory_optimizations(base)
        if hasattr(base, "set_progress_bar_config"):
            base.set_progress_bar_config(disable=True)

        refiner = None
        if config.SDXL_REFINER_ENABLED:
            try:
                from optimum.intel.openvino import OVStableDiffusionXLImg2ImgPipeline
            except Exception as exc:  # pragma: no cover - optional dependency
                raise ImportError(
                    "SDXL refiner requires OVStableDiffusionXLImg2ImgPipeline."
                ) from exc
            refiner_dir = config.SDXL_OV_REFINER_DIR
            _ensure_dir(refiner_dir, "SDXL refiner")
            refiner = _load_ov_pipeline(OVStableDiffusionXLImg2ImgPipeline, refiner_dir)
            self._apply_memory_optimizations(refiner)
            if hasattr(refiner, "set_progress_bar_config"):
                refiner.set_progress_bar_config(disable=True)

        return _SDXLOVPipelines(base=base, refiner=refiner, img2img=None)

    def _ensure_img2img(self, pipes: _SDXLOVPipelines) -> Any:
        if pipes.img2img is not None:
            return pipes.img2img
        try:
            from optimum.intel.openvino import OVStableDiffusionXLImg2ImgPipeline
        except Exception as exc:  # pragma: no cover - optional dependency
            raise ImportError(
                "OpenVINO SDXL edit requires OVStableDiffusionXLImg2ImgPipeline."
            ) from exc

        base_dir = config.SDXL_OV_BASE_DIR
        _ensure_dir(base_dir, "SDXL base")
        img2img = _load_ov_pipeline(OVStableDiffusionXLImg2ImgPipeline, base_dir)
        self._apply_memory_optimizations(img2img)
        if hasattr(img2img, "set_progress_bar_config"):
            img2img.set_progress_bar_config(disable=True)
        pipes.img2img = img2img
        return img2img

    def generate(
        self,
        params: GenerationParams,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> Image.Image:
        pipes = self.load()
        base = pipes.base
        refiner = pipes.refiner
        total_steps = params.steps * (2 if refiner else 1)

        def _wrap_progress(offset: int) -> Callable[[int, int], None]:
            def _progress(step: int, _total: int) -> None:
                progress_callback(step + offset, total_steps)

            return _progress

        generator = seed_everything(params.seed, "cpu")
        base_kwargs: dict[str, Any] = {
            "prompt": params.prompt,
            "num_inference_steps": params.steps,
            "width": params.width,
            "height": params.height,
            "generator": generator,
        }
        if params.negative_prompt:
            base_kwargs["negative_prompt"] = params.negative_prompt
        if params.guidance_scale is not None:
            base_kwargs["guidance_scale"] = params.guidance_scale
        if params.true_cfg_scale is not None:
            base_kwargs["true_cfg_scale"] = params.true_cfg_scale

        if refiner:
            base_kwargs["output_type"] = "latent"
            if progress_callback:
                base_kwargs = self._inject_progress_callback(
                    base, base_kwargs, params.steps, _wrap_progress(0)
                )
            base_kwargs = _filter_kwargs(base.__call__, base_kwargs)
            base_result = base(**base_kwargs)
            latents = _extract_latents(base_result)

            refiner_kwargs: dict[str, Any] = {
                "prompt": params.prompt,
                "image": latents,
                "num_inference_steps": params.steps,
                "denoising_start": config.SDXL_REFINER_DENOISING_START,
                "generator": generator,
            }
            if params.negative_prompt:
                refiner_kwargs["negative_prompt"] = params.negative_prompt
            if params.guidance_scale is not None:
                refiner_kwargs["guidance_scale"] = params.guidance_scale
            if progress_callback:
                refiner_kwargs = self._inject_progress_callback(
                    refiner, refiner_kwargs, params.steps, _wrap_progress(params.steps)
                )
            refiner_kwargs = _filter_kwargs(refiner.__call__, refiner_kwargs)
            result = refiner(**refiner_kwargs)
            return _normalize_image(result)

        if progress_callback:
            base_kwargs = self._inject_progress_callback(
                base, base_kwargs, params.steps, _wrap_progress(0)
            )
        base_kwargs = _filter_kwargs(base.__call__, base_kwargs)
        result = base(**base_kwargs)
        return _normalize_image(result)

    def edit(
        self,
        params: EditParams,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> Image.Image:
        if len(params.image_ids) != 1:
            raise ValueError("SDXL OpenVINO edit requires exactly one input image.")

        pipes = self.load()
        img2img = self._ensure_img2img(pipes)
        source = image_store.load_image(params.image_ids[0])
        prepared = _fit_image(source, config.MAX_WIDTH, config.MAX_HEIGHT)
        strength = (
            params.strength if params.strength is not None else DEFAULT_EDIT_STRENGTH
        )
        generator = seed_everything(params.seed, "cpu")

        kwargs: dict[str, Any] = {
            "prompt": params.prompt,
            "image": prepared,
            "num_inference_steps": params.steps,
            "strength": strength,
            "generator": generator,
        }
        if params.guidance_scale is not None:
            kwargs["guidance_scale"] = params.guidance_scale
        if params.true_cfg_scale is not None:
            kwargs["true_cfg_scale"] = params.true_cfg_scale
        if progress_callback:
            kwargs = self._inject_progress_callback(
                img2img, kwargs, params.steps, progress_callback
            )
        kwargs = _filter_kwargs(img2img.__call__, kwargs)
        result = img2img(**kwargs)
        return _normalize_image(result)
