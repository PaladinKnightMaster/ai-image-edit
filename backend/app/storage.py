from __future__ import annotations

from pathlib import Path
import shutil

from app import config


def _dir_size(path: Path) -> int:
    if not path.exists():
        return 0
    total = 0
    for item in path.rglob("*"):
        if item.is_file():
            try:
                total += item.stat().st_size
            except OSError:
                continue
    return total


def get_storage_info() -> dict[str, float | int | str]:
    data_root = (config.REPO_ROOT / "data").resolve()
    images_dir = data_root / "images"
    flux_outputs_dir = data_root / "flux2_outputs"
    db_path = config.DB_PATH
    db_size = db_path.stat().st_size if db_path.exists() else 0
    wal_size = (db_path.with_suffix(db_path.suffix + "-wal")).stat().st_size if db_path.with_suffix(db_path.suffix + "-wal").exists() else 0
    shm_size = (db_path.with_suffix(db_path.suffix + "-shm")).stat().st_size if db_path.with_suffix(db_path.suffix + "-shm").exists() else 0
    images_size = _dir_size(images_dir)
    flux_outputs_size = _dir_size(flux_outputs_dir)
    total_size = images_size + flux_outputs_size + db_size + wal_size + shm_size

    usage = shutil.disk_usage(data_root)
    return {
        "data_root": str(data_root),
        "images_bytes": images_size,
        "flux_outputs_bytes": flux_outputs_size,
        "db_bytes": db_size,
        "db_wal_bytes": wal_size,
        "db_shm_bytes": shm_size,
        "total_bytes": total_size,
        "disk_free_bytes": usage.free,
        "disk_total_bytes": usage.total,
    }
