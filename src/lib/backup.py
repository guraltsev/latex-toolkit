"""Timestamped backup helpers for destructive LaTeX tool writes.

This module is intentionally tiny so every mutating command can reuse the same
backup policy without inheriting any CLI behavior.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import shutil

DEFAULT_BACKUP_DIR = ".lt-backup"


def current_utc_timestamp() -> str:
    """Return a UTC timestamp formatted as ``YYYYMMDD:HHMMSS``."""

    return datetime.now(timezone.utc).strftime("%Y%m%d:%H%M%S")


def _resolve_backup_root(source_path: Path, backup_dir: str | Path) -> Path:
    backup_root = Path(backup_dir)
    if backup_root.is_absolute():
        return backup_root
    return source_path.parent / backup_root


def backup_file(source: str | Path, backup_dir: str | Path = DEFAULT_BACKUP_DIR) -> Path:
    """Copy ``source`` into ``backup_dir`` using the standard UTC naming policy.

    Relative backup directories are resolved against the source file's parent
    directory so that backups stay next to the document tree being edited.
    """

    source_path = Path(source).expanduser().resolve()
    if not source_path.exists():
        raise FileNotFoundError(f"Cannot back up missing file: {source}")
    if not source_path.is_file():
        raise IsADirectoryError(f"Cannot back up a directory: {source}")

    backup_root = _resolve_backup_root(source_path, backup_dir)
    backup_root.mkdir(parents=True, exist_ok=True)

    stamp = current_utc_timestamp()
    candidate = backup_root / f"{source_path.name}.backup.{stamp}"
    suffix = 1
    while candidate.exists():
        candidate = backup_root / f"{source_path.name}.backup.{stamp}.{suffix:02d}"
        suffix += 1

    shutil.copy2(source_path, candidate)
    return candidate


create_backup = backup_file
create_file_backup = backup_file
