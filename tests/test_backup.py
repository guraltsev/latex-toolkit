"""Protect timestamped file backups created through the public library API.

The test uses a real temporary source file and filesystem copy. Clock values
and implementation details other than the resulting backup are out of scope.
"""

from pathlib import Path
import re

from latex_toolkit.lib.backup import backup_file


def test_backup_file_creates_timestamped_copy_beside_source(tmp_path: Path) -> None:
    """A backup preserves the source content in the source's backup directory."""
    source = tmp_path / "affine_trick.tex"
    source.write_text("The original source.", encoding="utf-8")

    backup = backup_file(source)

    assert backup.parent == tmp_path / ".backup"
    assert re.fullmatch(r"affine_trick\.tex\.\d{8}-\d{6}\.bak", backup.name)
    assert backup.read_text(encoding="utf-8") == "The original source."
