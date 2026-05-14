"""Create timestamped backups for destructive LaTeX tool writes.

This module is intentionally tiny so every mutating command can reuse the same
backup policy without inheriting any CLI behavior.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import shutil

# Mutating commands store backups next to the edited source by default.
DEFAULT_BACKUP_DIR = ".backup"


def current_backup_timestamp() -> str:
    """Return a backup timestamp formatted as ``YYYYMMDD-HHMM``.

    Returns
    -------
    str
        Local timestamp used in backup filenames.
    """

    return datetime.now().strftime("%Y%m%d-%H%M")


def _resolve_backup_root(source_path: Path, backup_dir: str | Path) -> Path:
    """Return the absolute backup directory for ``source_path``."""

    backup_root = Path(backup_dir)
    if backup_root.is_absolute():
        return backup_root
    return source_path.parent / backup_root


def backup_file(source: str | Path, backup_dir: str | Path = DEFAULT_BACKUP_DIR) -> Path:
    """Copy ``source`` into ``backup_dir`` using the standard backup name.

    Relative backup directories are resolved against the source file's parent
    directory so that backups stay next to the document tree being edited.

    Parameters
    ----------
    source : str or pathlib.Path
        Existing file to copy before a destructive write.
    backup_dir : str or pathlib.Path
        Backup directory. Relative paths are resolved next to ``source``.

    Returns
    -------
    pathlib.Path
        Path to the created backup file.

    Raises
    ------
    FileNotFoundError
        ``source`` does not exist.
    IsADirectoryError
        ``source`` resolves to a directory.
    """

    source_path = Path(source).expanduser().resolve()
    if not source_path.exists():
        raise FileNotFoundError(f"Cannot back up missing file: {source}")
    if not source_path.is_file():
        raise IsADirectoryError(f"Cannot back up a directory: {source}")

    # Resolve and create the backup directory before choosing a candidate name,
    # so custom relative directories behave the same as the default.
    backup_root = _resolve_backup_root(source_path, backup_dir)
    backup_root.mkdir(parents=True, exist_ok=True)

    # The README-visible shape is ``YYYYMMDD-HHMM--filename``. If two backups
    # happen during the same minute, preserve both by adding a stable suffix.
    stamp = current_backup_timestamp()
    candidate = backup_root / f"{stamp}--{source_path.name}"
    suffix = 1
    while candidate.exists():
        candidate = backup_root / f"{stamp}--{source_path.name}.{suffix:02d}"
        suffix += 1

    shutil.copy2(source_path, candidate)
    return candidate


create_backup = backup_file
create_file_backup = backup_file
