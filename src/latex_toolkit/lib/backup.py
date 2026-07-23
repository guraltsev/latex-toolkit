"""Create timestamped backups before commands overwrite source files.

Mutating commands call ``backup_file(...)`` immediately before replacing an
input path. Backups are stored in a ``.backup`` directory beside the source.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from shutil import copy2


def backup_file(input_path: Path, *, timestamp: datetime | None = None) -> Path:
    """Copy a source file to its timestamped backup path.

    Parameters
    ----------
    input_path : pathlib.Path
        Existing source file to preserve before it is overwritten.
    timestamp : datetime.datetime, optional
        Time to embed in the backup name; the current local time is used when
        omitted.

    Returns
    -------
    pathlib.Path
        Path of the created backup file.

    Raises
    ------
    OSError
        The source cannot be copied or the backup directory cannot be created.
    """
    # Keep backups beside their source so moving a project keeps its recovery
    # history with the file it protects.
    backup_directory = input_path.parent / ".backup"
    backup_directory.mkdir(exist_ok=True)

    # Preserve every part of the original filename, including its extension,
    # before appending the sortable timestamp and backup marker.
    selected_time = timestamp or datetime.now()
    backup_path = backup_directory / (
        f"{input_path.name}.{selected_time:%Y%m%d-%H%M%S}.bak"
    )
    return Path(copy2(input_path, backup_path))
