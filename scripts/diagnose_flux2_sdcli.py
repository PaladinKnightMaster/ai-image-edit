from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv  # type: ignore

    _dotenv_path = os.getenv("DOTENV_PATH")
    if _dotenv_path:
        load_dotenv(Path(_dotenv_path).expanduser(), override=False)
    else:
        load_dotenv(Path(__file__).resolve().parents[1] / "backend" / ".env", override=False)
except Exception:
    pass


MIN_GGUF_BYTES = 1 * 1024 * 1024 * 1024
MIN_VAE_BYTES = 100 * 1024 * 1024


def _root() -> Path:
    return Path(__file__).resolve().parents[1]


def _resolve_path(value: str | Path, base: Path) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = (base / path).resolve()
    return path


def _format_size(bytes_value: int) -> str:
    mb = bytes_value / (1024 * 1024)
    gb = bytes_value / (1024 * 1024 * 1024)
    return f"{mb:.1f} MB / {gb:.2f} GB"


def _check_size(path: Path, min_bytes: int, label: str) -> list[str]:
    errors = []
    if not path.exists():
        errors.append(f"{label} missing at {path}")
        return errors
    size = path.stat().st_size
    if size < min_bytes:
        errors.append(f"{label} too small ({_format_size(size)}) at {path}")
    return errors


def _resolve_sdcli_path() -> Path | None:
    candidate = os.getenv("FLUX2_SDCLI_PATH", "sd")
    if os.path.isabs(candidate):
        return Path(candidate)
    found = shutil.which(candidate)
    if found:
        return Path(found)
    repo_candidate = _resolve_path(candidate, _root())
    return repo_candidate if repo_candidate.exists() else None


def main() -> int:
    repo_root = _root()
    sdcli_path = _resolve_sdcli_path()
    diffusion = _resolve_path(
        os.getenv(
            "FLUX2_DIFFUSION_GGUF",
            "models/flux2_klein_9b_gguf/diffusion_model/flux-2-klein-9b-Q4_K_M.gguf",
        ),
        repo_root,
    )
    vae = _resolve_path(
        os.getenv(
            "FLUX2_VAE",
            "models/flux2_klein_9b_gguf/vae/flux2-vae.safetensors",
        ),
        repo_root,
    )
    llm = _resolve_path(
        os.getenv(
            "FLUX2_LLM_GGUF",
            "models/flux2_klein_9b_gguf/text_encoder_gguf/Qwen3-8B-Q6_K.gguf",
        ),
        repo_root,
    )

    errors: list[str] = []
    if sdcli_path is None or not sdcli_path.exists():
        errors.append("sd-cli not found. Set FLUX2_SDCLI_PATH to sd.exe or sd-cli.")
    errors.extend(_check_size(diffusion, MIN_GGUF_BYTES, "Diffusion GGUF"))
    errors.extend(_check_size(llm, MIN_GGUF_BYTES, "LLM GGUF"))
    errors.extend(_check_size(vae, MIN_VAE_BYTES, "VAE"))

    if errors:
        print("Diagnostics failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"sd-cli: {sdcli_path}")
    print(f"diffusion: {diffusion} ({_format_size(diffusion.stat().st_size)})")
    print(f"llm: {llm} ({_format_size(llm.stat().st_size)})")
    print(f"vae: {vae} ({_format_size(vae.stat().st_size)})")

    try:
        result = subprocess.run(
            [str(sdcli_path), "--help"],
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception as exc:
        print(f"Failed to run sd-cli --help: {exc}")
        return 1

    output = (result.stdout or "") + "\n" + (result.stderr or "")
    lines = [line for line in output.splitlines() if line.strip()]
    print("sd-cli --help (first 50 lines):")
    for line in lines[:50]:
        print(line)
    if result.returncode != 0:
        print(f"sd-cli exited with code {result.returncode}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
