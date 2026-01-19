from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from app import config


@dataclass(frozen=True)
class ModelSpec:
    model_id: str
    repo_id: str


MODEL_SPECS = (
    ModelSpec("qwen-image-2512", "Qwen/Qwen-Image-2512"),
    ModelSpec("qwen-image-edit-2511", "Qwen/Qwen-Image-Edit-2511"),
)

MODEL_MAP: Dict[str, ModelSpec] = {spec.model_id: spec for spec in MODEL_SPECS}


def _repo_parts(repo_id: str) -> tuple[str, str]:
    if "/" not in repo_id:
        raise ValueError(f"Invalid repo_id '{repo_id}'. Expected org/name.")
    return repo_id.split("/", 1)


def _base_dir(spec: ModelSpec) -> Path:
    org, name = _repo_parts(spec.repo_id)
    return config.MODEL_ROOT / org / name


def _candidate_dir(base_dir: Path) -> tuple[Path, Optional[str], Optional[str]]:
    revision = config.MODEL_REVISION
    if revision:
        candidate = base_dir / revision
        if candidate.exists():
            return candidate, revision, None
        return candidate, revision, f"Revision '{revision}' not found."

    main_dir = base_dir / "main"
    if main_dir.exists():
        return main_dir, "main", None

    if base_dir.exists():
        revisions = sorted([path for path in base_dir.iterdir() if path.is_dir()])
        if len(revisions) == 1:
            return revisions[0], revisions[0].name, None
        if len(revisions) > 1:
            return (
                main_dir,
                None,
                "Multiple revisions found. Set MODEL_REVISION to pick one.",
            )
        return main_dir, None, "No revision directories found."

    return main_dir, None, "Model directory not found."


def resolve_model_path(model_id: str) -> Path:
    spec = MODEL_MAP.get(model_id)
    if not spec:
        raise KeyError(f"Unknown model id '{model_id}'.")

    base_dir = _base_dir(spec)
    candidate, _, detail = _candidate_dir(base_dir)
    if not candidate.exists():
        hint = (
            f"Local model files for '{model_id}' are missing at {candidate}. "
            "Run: python scripts/mirror_models.py"
        )
        if detail:
            hint = f"{hint} ({detail})"
        raise FileNotFoundError(hint)

    if detail and "Multiple revisions" in detail:
        raise FileNotFoundError(
            f"Multiple revisions found for '{model_id}'. Set MODEL_REVISION to select one."
        )

    return candidate


def get_model_status(model_id: str) -> dict:
    spec = MODEL_MAP.get(model_id)
    if not spec:
        raise KeyError(f"Unknown model id '{model_id}'.")
    base_dir = _base_dir(spec)
    candidate, revision, detail = _candidate_dir(base_dir)
    present = candidate.exists()
    return {
        "id": spec.model_id,
        "present": present,
        "local_path": str(candidate),
        "revision": revision,
        "detail": None if present else detail,
    }


def list_models() -> List[dict]:
    return [get_model_status(spec.model_id) for spec in MODEL_SPECS]
