from __future__ import annotations

import inspect
import logging
import os
import shlex
import shutil
import subprocess
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4

from PIL import Image

from app import config, images as image_store
from inference.base import EditParams, GenerationParams, Runner

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Flux2Assets:
    model_dir: Path
    diffusion_gguf: Path
    vae: Path
    text_encoder: Path
    text_encoder_gguf: Path | None
    llm_gguf: Path | None


def _assets() -> Flux2Assets:
    text_encoder_gguf = (
        Path(config.FLUX2_TEXT_ENCODER_GGUF).resolve()
        if config.FLUX2_TEXT_ENCODER_GGUF
        else None
    )
    llm_gguf = config.FLUX2_LLM_GGUF if config.FLUX2_LLM_GGUF else None
    return Flux2Assets(
        model_dir=config.FLUX2_MODEL_DIR,
        diffusion_gguf=config.FLUX2_DIFFUSION_GGUF,
        vae=config.FLUX2_VAE,
        text_encoder=config.FLUX2_TEXT_ENCODER,
        text_encoder_gguf=text_encoder_gguf,
        llm_gguf=llm_gguf,
    )


def _validate_assets(use_py_bindings: bool, use_sdcli: bool) -> Flux2Assets:
    assets = _assets()
    missing: list[str] = []
    if not assets.diffusion_gguf.exists():
        missing.append(str(assets.diffusion_gguf))
    if not assets.vae.exists():
        missing.append(str(assets.vae))

    llm_exists = False
    if assets.llm_gguf is not None and assets.llm_gguf.exists():
        llm_exists = True
    if assets.text_encoder_gguf is not None and assets.text_encoder_gguf.exists():
        llm_exists = True

    if use_py_bindings:
        text_encoder_exists = assets.text_encoder.exists()
        if not text_encoder_exists and not llm_exists:
            missing.append(str(assets.text_encoder))

    if use_sdcli and not llm_exists:
        missing.append("FLUX2_LLM_GGUF (required for sd-cli)")

    if missing:
        hint = "Missing FLUX.2 klein assets:\n" + "\n".join(f"- {item}" for item in missing)
        hint += "\nRun: scripts\\fetch_flux2_klein_gguf.ps1 (or place files manually)."
        raise FileNotFoundError(hint)
    return assets


def _resolve_sdcli_path() -> str:
    candidate = config.FLUX2_SDCLI_PATH
    if os.path.isabs(candidate):
        return candidate
    found = shutil.which(candidate)
    return found or candidate


def _split_extra_args(extra_args: str) -> list[str]:
    if not extra_args:
        return []
    return shlex.split(extra_args, posix=os.name != "nt")


_ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
_SDCLI_PROGRESS_RE = re.compile(r"\|\s*[=><]+\s*\|\s*(\d+)\s*/\s*(\d+)")


def _strip_ansi(text: str) -> str:
    return _ANSI_ESCAPE_RE.sub("", text)


def _filter_kwargs(callable_obj: Any, kwargs: dict[str, Any]) -> dict[str, Any]:
    try:
        signature = inspect.signature(callable_obj)
    except (TypeError, ValueError):
        return kwargs
    valid = set(signature.parameters.keys())
    return {key: value for key, value in kwargs.items() if key in valid}


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
    raise RuntimeError("Unexpected image result from FLUX2 backend.")


class _Flux2PythonBackend:
    def __init__(self, assets: Flux2Assets):
        try:
            import stable_diffusion_cpp  # type: ignore
        except Exception as exc:  # pragma: no cover - depends on optional install
            raise ImportError("stable-diffusion-cpp-python not installed.") from exc

        cls = getattr(stable_diffusion_cpp, "StableDiffusion", None)
        if cls is None:
            cls = getattr(stable_diffusion_cpp, "StableDiffusionCpp", None)
        if cls is None:
            raise ImportError("stable-diffusion-cpp-python bindings missing StableDiffusion class.")

        param_names = set(inspect.signature(cls.__init__).parameters.keys())
        diffusion_path = str(assets.diffusion_gguf)
        vae_path = str(assets.vae)
        if assets.llm_gguf is not None and assets.llm_gguf.exists():
            text_encoder_path = str(assets.llm_gguf)
        elif assets.text_encoder_gguf is not None and assets.text_encoder_gguf.exists():
            text_encoder_path = str(assets.text_encoder_gguf)
        else:
            if not config.FLUX2_ALLOW_SAFETENSORS_LLM:
                raise RuntimeError(
                    "FLUX2 pybindings requires a GGUF LLM on Windows. "
                    "Set FLUX2_LLM_GGUF to a GGUF file."
                )
            text_encoder_path = str(assets.text_encoder)

        kwargs: dict[str, Any] = {}
        has_diffusion = False
        if "diffusion_model_path" in param_names:
            kwargs["diffusion_model_path"] = diffusion_path
            has_diffusion = True
        elif "model_path" in param_names:
            kwargs["model_path"] = diffusion_path
            has_diffusion = True

        has_vae = False
        if "vae_path" in param_names:
            kwargs["vae_path"] = vae_path
            has_vae = True

        has_text_encoder = False
        if "llm_path" in param_names:
            kwargs["llm_path"] = text_encoder_path
            has_text_encoder = True

        if "n_threads" in param_names:
            kwargs["n_threads"] = max(1, (os.cpu_count() or 2) - 1)
        if "rng_type" in param_names:
            kwargs["rng_type"] = config.FLUX2_RNG_TYPE
        if "sampler_rng_type" in param_names:
            kwargs["sampler_rng_type"] = config.FLUX2_SAMPLER_RNG_TYPE
        if "prediction" in param_names:
            kwargs["prediction"] = config.FLUX2_PREDICTION
        if "verbose" in param_names:
            kwargs["verbose"] = False

        if not has_diffusion or not has_vae:
            raise ImportError(
                "stable-diffusion-cpp-python bindings missing diffusion_model_path/model_path "
                "or vae_path."
            )
        if not has_text_encoder:
            raise ImportError(
                "stable-diffusion-cpp-python bindings missing llm_path for FLUX2 text encoder."
            )

        self._client = cls(**kwargs)

    @property
    def backend_name(self) -> str:
        return "pybindings"

    def txt2img(
        self,
        prompt: str,
        negative_prompt: str | None,
        width: int,
        height: int,
        steps: int,
        guidance: float,
        seed: int,
    ) -> Image.Image:
        method = getattr(self._client, "generate_image", None)
        if method is None:
            raise RuntimeError("stable-diffusion-cpp-python generate_image method not found.")

        cfg_scale = 1.0
        payload: dict[str, Any] = {
            "prompt": prompt,
            "negative_prompt": negative_prompt or "",
            "width": width,
            "height": height,
            "sample_steps": steps,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "guidance": guidance,
            "seed": seed,
        }
        payload = _filter_kwargs(method, payload)
        return _normalize_image(method(**payload))

    def img2img(
        self,
        prompt: str,
        negative_prompt: str | None,
        init_image: Image.Image,
        steps: int,
        guidance: float,
        seed: int,
        strength: float,
    ) -> Image.Image:
        method = getattr(self._client, "generate_image", None)
        if method is None:
            raise RuntimeError("stable-diffusion-cpp-python generate_image method not found.")

        cfg_scale = 1.0
        payload: dict[str, Any] = {
            "prompt": prompt,
            "negative_prompt": negative_prompt or "",
            "init_image": init_image,
            "image": init_image,
            "sample_steps": steps,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "guidance": guidance,
            "seed": seed,
            "strength": strength,
        }
        payload = _filter_kwargs(method, payload)
        return _normalize_image(method(**payload))


class _Flux2SdCliBackend:
    def __init__(self, assets: Flux2Assets):
        self._assets = assets
        self._sdcli_path = _resolve_sdcli_path()

    @property
    def backend_name(self) -> str:
        return "sd-cli"

    def _resolve_llm(self) -> Path:
        if self._assets.llm_gguf is not None and self._assets.llm_gguf.exists():
            return self._assets.llm_gguf
        if self._assets.text_encoder_gguf is not None and self._assets.text_encoder_gguf.exists():
            return self._assets.text_encoder_gguf
        raise RuntimeError(
            "sd-cli backend requires FLUX2_LLM_GGUF (or FLUX2_TEXT_ENCODER_GGUF) for --llm."
        )

    def _run(
        self,
        args: list[str],
        output_dir: Path,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        log_path = output_dir / "sdcli.log"
        sampling_active = False
        last_progress: tuple[int, int] | None = None
        with log_path.open("w", encoding="utf-8") as log_file:
            log_file.write(f"command: {' '.join(args)}\n\noutput:\n")
            process = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
            )
            assert process.stdout is not None
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if not line:
                    continue
                clean_line = _strip_ansi(line)
                log_file.write(clean_line)
                log_file.flush()

                lower_line = clean_line.lower()
                if "generating image" in lower_line or "txt2img" in lower_line or "img2img" in lower_line:
                    sampling_active = True
                if sampling_active and progress_callback:
                    match = _SDCLI_PROGRESS_RE.search(clean_line)
                    if match:
                        step = int(match.group(1))
                        total = int(match.group(2))
                        progress = (step, total)
                        if progress != last_progress:
                            last_progress = progress
                            progress_callback(step, total)

            return_code = process.wait()
            log_file.write(f"\nexit_code={return_code}\n")
        if return_code != 0:
            raise RuntimeError(f"sd-cli failed (exit {return_code}). See {log_path}.")

    def _build_args(
        self,
        prompt: str,
        negative_prompt: str | None,
        width: int,
        height: int,
        steps: int,
        guidance: float,
        seed: int,
        output_path: Path,
        init_image: Path | None = None,
        strength: float | None = None,
    ) -> list[str]:
        llm_path = self._resolve_llm()

        args = [
            self._sdcli_path,
            "--diffusion-model",
            str(self._assets.diffusion_gguf),
            "--vae",
            str(self._assets.vae),
            "--llm",
            str(llm_path),
            "-p",
            prompt,
            "--steps",
            str(steps),
            "--cfg-scale",
            str(guidance),
            "--seed",
            str(seed),
            "-W",
            str(width),
            "-H",
            str(height),
            "-o",
            str(output_path),
        ]
        if negative_prompt:
            args += ["--negative-prompt", negative_prompt]
        if init_image is not None:
            args += ["-r", str(init_image)]
        if strength is not None:
            args += ["--strength", str(strength)]
        args += _split_extra_args(config.FLUX2_SDCLI_EXTRA_ARGS)
        return args

    def txt2img(
        self,
        prompt: str,
        negative_prompt: str | None,
        width: int,
        height: int,
        steps: int,
        guidance: float,
        seed: int,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> Image.Image:
        run_id = uuid4().hex
        output_dir = config.REPO_ROOT / "data" / "flux2_outputs" / run_id
        output_path = output_dir / "out.png"
        args = self._build_args(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            steps=steps,
            guidance=guidance,
            seed=seed,
            output_path=output_path,
        )
        self._run(args, output_dir, progress_callback=progress_callback)
        with Image.open(output_path) as image:
            image.load()
            return image.copy()

    def img2img(
        self,
        prompt: str,
        negative_prompt: str | None,
        init_image: Image.Image,
        steps: int,
        guidance: float,
        seed: int,
        strength: float,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> Image.Image:
        run_id = uuid4().hex
        output_dir = config.REPO_ROOT / "data" / "flux2_outputs" / run_id
        output_path = output_dir / "out.png"
        input_path = output_dir / "input.png"
        output_dir.mkdir(parents=True, exist_ok=True)
        init_image.save(input_path, format="PNG")
        args = self._build_args(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=init_image.width,
            height=init_image.height,
            steps=steps,
            guidance=guidance,
            seed=seed,
            output_path=output_path,
            init_image=input_path,
            strength=strength,
        )
        self._run(args, output_dir, progress_callback=progress_callback)
        with Image.open(output_path) as image:
            image.load()
            return image.copy()


class Flux2KleinGGUFRunner(Runner):
    id = "flux2-klein-9b-gguf"
    label = "FLUX.2 klein 9B (GGUF) - fast"
    capabilities = {"t2i", "edit"}
    defaults = {
        "steps": config.FLUX2_DEFAULT_STEPS,
        "width": config.FLUX2_DEFAULT_SIZE,
        "height": config.FLUX2_DEFAULT_SIZE,
        "guidance_scale": config.FLUX2_DEFAULT_GUIDANCE,
        "strength": config.FLUX2_DEFAULT_STRENGTH,
    }
    manual_review = True

    def __init__(self) -> None:
        super().__init__()
        self._backend_name = "unknown"
        self._pybindings_disabled = False

    @property
    def backend_name(self) -> str:
        return self._backend_name

    def model_status(self) -> dict[str, Any]:
        assets = _assets()
        present = assets.diffusion_gguf.exists() and assets.vae.exists()
        text_encoder_ok = assets.text_encoder.exists()
        if assets.text_encoder_gguf is not None and assets.text_encoder_gguf.exists():
            text_encoder_ok = True
        if assets.llm_gguf is not None and assets.llm_gguf.exists():
            text_encoder_ok = True
        if not text_encoder_ok:
            present = False
        return {
            "present": present,
            "local_path": str(assets.model_dir),
            "revision": None,
        }

    def _load_pipeline(self) -> Any:
        use_py = config.FLUX2_USE_PY_BINDINGS
        use_sdcli = config.FLUX2_USE_SDCLI_FALLBACK

        if use_py and not self._pybindings_disabled:
            try:
                assets = _validate_assets(use_py_bindings=True, use_sdcli=False)
                backend = _Flux2PythonBackend(assets)
                self._backend_name = backend.backend_name
                return backend
            except Exception as exc:
                logger.warning("FLUX2 py bindings unavailable: %s", exc)
                if not use_sdcli:
                    raise

        if use_sdcli:
            assets = _validate_assets(use_py_bindings=False, use_sdcli=True)
            backend = _Flux2SdCliBackend(assets)
            self._backend_name = backend.backend_name
            return backend

        raise RuntimeError("No FLUX2 backend available. Enable bindings or sd-cli fallback.")

    def _fallback_to_sdcli(self, reason: Exception) -> _Flux2SdCliBackend:
        if not config.FLUX2_USE_SDCLI_FALLBACK:
            raise reason
        logger.warning(
            "FLUX2 py bindings failed (%s). Falling back to sd-cli backend.",
            reason,
        )
        self._pybindings_disabled = True
        assets = _validate_assets(use_py_bindings=False, use_sdcli=True)
        backend = _Flux2SdCliBackend(assets)
        self._backend_name = backend.backend_name
        self._pipe = backend
        return backend

    def generate(
        self,
        params: GenerationParams,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> Image.Image:
        pipe = self.load()
        guidance = (
            params.guidance_scale
            if params.guidance_scale is not None
            else config.FLUX2_DEFAULT_GUIDANCE
        )
        payload = dict(
            prompt=params.prompt,
            negative_prompt=params.negative_prompt,
            width=params.width,
            height=params.height,
            steps=params.steps,
            guidance=guidance,
            seed=params.seed,
        )
        try:
            signature = inspect.signature(pipe.txt2img)
            if progress_callback and "progress_callback" in signature.parameters:
                payload["progress_callback"] = progress_callback
        except (TypeError, ValueError):
            pass
        try:
            return pipe.txt2img(**payload)
        except Exception as exc:
            if isinstance(pipe, _Flux2PythonBackend):
                pipe = self._fallback_to_sdcli(exc)
                payload = dict(
                    prompt=params.prompt,
                    negative_prompt=params.negative_prompt,
                    width=params.width,
                    height=params.height,
                    steps=params.steps,
                    guidance=guidance,
                    seed=params.seed,
                )
                if progress_callback:
                    payload["progress_callback"] = progress_callback
                return pipe.txt2img(**payload)
            raise

    def edit(
        self,
        params: EditParams,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> Image.Image:
        pipe = self.load()
        if len(params.image_ids) != 1:
            raise ValueError("FLUX2 edit requires exactly one input image.")
        input_image = image_store.load_image(params.image_ids[0])
        guidance = (
            params.guidance_scale
            if params.guidance_scale is not None
            else config.FLUX2_DEFAULT_GUIDANCE
        )
        strength = params.strength if params.strength is not None else config.FLUX2_DEFAULT_STRENGTH
        payload = dict(
            prompt=params.prompt,
            negative_prompt=None,
            init_image=input_image,
            steps=params.steps,
            guidance=guidance,
            seed=params.seed,
            strength=strength,
        )
        try:
            signature = inspect.signature(pipe.img2img)
            if progress_callback and "progress_callback" in signature.parameters:
                payload["progress_callback"] = progress_callback
        except (TypeError, ValueError):
            pass
        try:
            return pipe.img2img(**payload)
        except Exception as exc:
            if isinstance(pipe, _Flux2PythonBackend):
                pipe = self._fallback_to_sdcli(exc)
                payload = dict(
                    prompt=params.prompt,
                    negative_prompt=None,
                    init_image=input_image,
                    steps=params.steps,
                    guidance=guidance,
                    seed=params.seed,
                    strength=strength,
                )
                if progress_callback:
                    payload["progress_callback"] = progress_callback
                return pipe.img2img(**payload)
            raise


def flux2_diagnostics() -> dict[str, Any]:
    assets = _assets()
    missing: list[str] = []
    for path in (assets.diffusion_gguf, assets.vae, assets.text_encoder):
        if not path.exists():
            missing.append(str(path))
    if assets.text_encoder_gguf and not assets.text_encoder_gguf.exists():
        missing.append(str(assets.text_encoder_gguf))

    py_bindings = {"available": False, "error": None}
    try:
        import stable_diffusion_cpp  # type: ignore

        py_bindings["available"] = True
    except Exception as exc:
        py_bindings["error"] = str(exc)

    sdcli_path = _resolve_sdcli_path()
    sdcli_available = bool(shutil.which(sdcli_path) or Path(sdcli_path).exists())

    return {
        "assets": {
            "model_dir": str(assets.model_dir),
            "missing": missing,
        },
        "py_bindings": py_bindings,
        "sdcli": {
            "path": sdcli_path,
            "available": sdcli_available,
        },
        "config": {
            "use_py_bindings": config.FLUX2_USE_PY_BINDINGS,
            "use_sdcli_fallback": config.FLUX2_USE_SDCLI_FALLBACK,
        },
    }
