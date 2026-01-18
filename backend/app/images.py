from __future__ import annotations

from pathlib import Path
import time
from uuid import uuid4

from PIL import Image

from app import config, db

IMAGE_ROOT = (config.REPO_ROOT / "data" / "images").resolve()
IMAGE_ROOT.mkdir(parents=True, exist_ok=True)


def _image_path(image_id: str) -> Path:
    return IMAGE_ROOT / f"{image_id}.png"


def get_image_path(image_id: str) -> Path:
    return _image_path(image_id)


def _record_metadata(
    *,
    image_id: str,
    filename: str | None,
    source: str | None,
    created_at: int | None,
    width: int | None,
    height: int | None,
    size_bytes: int | None,
    content_type: str | None,
    job_id: str | None,
    run_id: str | None,
) -> None:
    try:
        with db.get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO images (
                    id, filename, source, created_at, width, height, size_bytes, content_type, job_id, run_id
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    image_id,
                    filename,
                    source,
                    created_at,
                    width,
                    height,
                    size_bytes,
                    content_type,
                    job_id,
                    run_id,
                ),
            )
            conn.commit()
    except Exception:
        return


def save_image(
    image: Image.Image,
    *,
    filename: str | None = None,
    source: str | None = None,
    content_type: str | None = None,
    job_id: str | None = None,
    run_id: str | None = None,
    created_at: int | None = None,
    size_bytes: int | None = None,
) -> tuple[str, Path]:
    image_id = uuid4().hex
    path = _image_path(image_id)
    rgb = image.convert("RGB")
    rgb.save(path, format="PNG")
    if created_at is None:
        created_at = int(time.time() * 1000)
    _record_metadata(
        image_id=image_id,
        filename=filename,
        source=source,
        created_at=created_at,
        width=rgb.width,
        height=rgb.height,
        size_bytes=size_bytes or path.stat().st_size,
        content_type=content_type or "image/png",
        job_id=job_id,
        run_id=run_id,
    )
    return image_id, path


def get_image_metadata(image_id: str) -> dict | None:
    try:
        with db.get_connection() as conn:
            row = conn.execute("SELECT * FROM images WHERE id = ?", (image_id,)).fetchone()
            if not row:
                return None
            return dict(row)
    except Exception:
        return None


def load_image(image_id: str) -> Image.Image:
    path = _image_path(image_id)
    if not path.exists():
        raise FileNotFoundError(f"Image '{image_id}' not found.")
    with Image.open(path) as image:
        image.load()
        return image.convert("RGB")
