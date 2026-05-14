"""Tests for the observable backup naming and collision policy.

The tests use real temporary files and mock only the clock so the timestamped
filename is deterministic. Directory permission failures and platform-specific
filesystem behavior are out of scope.
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
TOOLKIT = SRC / "latex-toolkit"
if str(TOOLKIT) not in sys.path:
    sys.path.insert(0, str(TOOLKIT))

from lib.backup import backup_file  # noqa: E402


class BackupTests(TestCase):
    def test_backup_uses_requested_name_shape(self) -> None:
        """Default backups use the README-documented directory and filename shape."""

        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            source = work / "paper.tex"
            source.write_text("hello", encoding="utf-8")

            with patch("lib.backup.current_backup_timestamp", return_value="20260412-0315"):
                backup_path = backup_file(source)

            self.assertEqual(backup_path.name, "20260412-0315--paper.tex")
            self.assertEqual(backup_path.parent.name, ".backup")
            self.assertEqual(backup_path.read_text(encoding="utf-8"), "hello")

    def test_backup_collision_adds_numeric_suffix(self) -> None:
        """Multiple backups in the same minute preserve both copies."""

        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            source = work / "paper.tex"
            source.write_text("hello", encoding="utf-8")

            with patch("lib.backup.current_backup_timestamp", return_value="20260412-0315"):
                first = backup_file(source)
                second = backup_file(source)

            self.assertEqual(first.name, "20260412-0315--paper.tex")
            self.assertEqual(second.name, "20260412-0315--paper.tex.01")
