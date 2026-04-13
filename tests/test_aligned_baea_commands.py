from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "src" / "lt_cli.py"
FIXTURES = ROOT / "tests" / "fixtures"


class AlignedBaeaCommandTests(TestCase):
    def run_cli(self, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CLI), *args],
            cwd=str(cwd) if cwd is not None else None,
            text=True,
            capture_output=True,
            check=False,
        )

    def _copy_fixture_input(self, fixture_dir: Path, destination_dir: Path) -> tuple[Path, str, str]:
        source_input = fixture_dir / "input.tex"
        expected_output = fixture_dir / "output.tex"
        copied_input = destination_dir / source_input.name
        shutil.copy2(source_input, copied_input)
        return (
            copied_input,
            source_input.read_text(encoding="utf-8"),
            expected_output.read_text(encoding="utf-8"),
        )

    def test_aligned2baea_fixture_overwrite_matches_expected_output_and_creates_backup(self) -> None:
        fixture_dir = FIXTURES / "aligned2baea" / "forward"
        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            copied_input, original_text, expected_text = self._copy_fixture_input(fixture_dir, work)

            result = self.run_cli("aligned2baea", str(copied_input))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(copied_input.read_text(encoding="utf-8"), expected_text)
            backup_dir = work / ".lt-backup"
            backups = sorted(backup_dir.iterdir())
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), original_text)

    def test_aligned2baea_reverse_fixture_overwrite_matches_expected_output_and_creates_backup(self) -> None:
        fixture_dir = FIXTURES / "aligned2baea" / "reverse"
        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            copied_input, original_text, expected_text = self._copy_fixture_input(fixture_dir, work)

            result = self.run_cli("aligned2baea", str(copied_input), "--reverse")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(copied_input.read_text(encoding="utf-8"), expected_text)
            backup_dir = work / ".lt-backup"
            backups = sorted(backup_dir.iterdir())
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), original_text)

    def test_baea2aligned_fixture_overwrite_matches_expected_output_and_creates_backup(self) -> None:
        fixture_dir = FIXTURES / "aligned2baea" / "reverse"
        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            copied_input, original_text, expected_text = self._copy_fixture_input(fixture_dir, work)

            result = self.run_cli("baea2aligned", str(copied_input))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(copied_input.read_text(encoding="utf-8"), expected_text)
            backup_dir = work / ".lt-backup"
            backups = sorted(backup_dir.iterdir())
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), original_text)

    def test_aligned2baea_output_option_uses_expected_output_without_touching_source(self) -> None:
        fixture_dir = FIXTURES / "aligned2baea" / "forward"
        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            copied_input, original_text, expected_text = self._copy_fixture_input(fixture_dir, work)
            output_path = work / "converted.tex"

            result = self.run_cli("aligned2baea", str(copied_input), "-o", str(output_path))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(copied_input.read_text(encoding="utf-8"), original_text)
            self.assertEqual(output_path.read_text(encoding="utf-8"), expected_text)
            self.assertFalse((work / ".lt-backup").exists())
