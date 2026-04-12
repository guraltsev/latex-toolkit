from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lib.backup import backup_file  # noqa: E402


class BackupTests(TestCase):
    def test_backup_uses_requested_name_shape(self) -> None:
        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            source = work / "paper.tex"
            source.write_text("hello", encoding="utf-8")

            with patch("lib.backup.current_utc_timestamp", return_value="20260412:031500"):
                backup_path = backup_file(source)

            self.assertEqual(backup_path.name, "paper.tex.backup.20260412:031500")
            self.assertEqual(backup_path.parent.name, ".lt-backup")
            self.assertEqual(backup_path.read_text(encoding="utf-8"), "hello")

    def test_backup_collision_adds_numeric_suffix(self) -> None:
        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            source = work / "paper.tex"
            source.write_text("hello", encoding="utf-8")

            with patch("lib.backup.current_utc_timestamp", return_value="20260412:031500"):
                first = backup_file(source)
                second = backup_file(source)

            self.assertEqual(first.name, "paper.tex.backup.20260412:031500")
            self.assertEqual(second.name, "paper.tex.backup.20260412:031500.01")
