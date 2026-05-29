"""Command tests for display-math and equation conversions.

The tests invoke real CLI commands against fixture files and check observable
file contents plus backup behavior. Low-level parser details and unrelated
LaTeX environments are out of scope.
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
import shutil
import subprocess
import sys

from test_support import FIXTURES_ROOT, pythonpath_env


class DisplayMathEquationCommandTests(TestCase):
    def run_cli(self, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        command_name, *command_args = args
        return subprocess.run(
            [sys.executable, "-m", f"latex_toolkit.commands.{command_name}", *command_args],
            cwd=str(cwd) if cwd is not None else None,
            env=pythonpath_env(),
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

    def test_eqn_star2dmath_fixture_overwrite_matches_expected_output_and_creates_backup(self) -> None:
        """Forward equation* conversion overwrites fixtures and backs up originals."""

        fixture_dir = FIXTURES_ROOT / "eqn-star2dmath" / "forward"
        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            copied_input, original_text, expected_text = self._copy_fixture_input(fixture_dir, work)

            result = self.run_cli("eqn_star2dmath", str(copied_input))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(copied_input.read_text(encoding="utf-8"), expected_text)
            backup_dir = work / ".backup"
            backups = sorted(backup_dir.iterdir())
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), original_text)

    def test_eqn_star2dmath_reverse_fixture_overwrite_matches_expected_output_and_creates_backup(self) -> None:
        """Reverse equation* conversion overwrites fixtures and backs up originals."""

        fixture_dir = FIXTURES_ROOT / "eqn-star2dmath" / "reverse"
        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            copied_input, original_text, expected_text = self._copy_fixture_input(fixture_dir, work)

            result = self.run_cli("eqn_star2dmath", str(copied_input), "--reverse")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(copied_input.read_text(encoding="utf-8"), expected_text)
            backup_dir = work / ".backup"
            backups = sorted(backup_dir.iterdir())
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), original_text)

    def test_dmath2eqn_star_fixture_overwrite_matches_expected_output_and_creates_backup(self) -> None:
        """The dmath2eqn-star alias rewrites display math with the shared write policy."""

        fixture_dir = FIXTURES_ROOT / "eqn-star2dmath" / "reverse"
        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            copied_input, original_text, expected_text = self._copy_fixture_input(fixture_dir, work)

            result = self.run_cli("dmath2eqn_star", str(copied_input))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(copied_input.read_text(encoding="utf-8"), expected_text)
            backup_dir = work / ".backup"
            backups = sorted(backup_dir.iterdir())
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), original_text)

    def test_eqn_star2dmath_output_option_uses_expected_output_without_touching_source(self) -> None:
        """Writing equation* conversion output separately preserves the source."""

        fixture_dir = FIXTURES_ROOT / "eqn-star2dmath" / "forward"
        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            copied_input, original_text, expected_text = self._copy_fixture_input(fixture_dir, work)
            output_path = work / "converted.tex"

            result = self.run_cli("eqn_star2dmath", str(copied_input), "-o", str(output_path))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(copied_input.read_text(encoding="utf-8"), original_text)
            self.assertEqual(output_path.read_text(encoding="utf-8"), expected_text)
            self.assertFalse((work / ".backup").exists())

    def test_eqn2dmath_eqnum_fixture_overwrite_matches_expected_output_and_creates_backup(self) -> None:
        """Forward numbered-equation conversion overwrites and backs up fixtures."""

        fixture_dir = FIXTURES_ROOT / "eqn2dmath-eqnum" / "forward"
        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            copied_input, original_text, expected_text = self._copy_fixture_input(fixture_dir, work)

            result = self.run_cli("eqn2dmath_eqnum", str(copied_input))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(copied_input.read_text(encoding="utf-8"), expected_text)
            backup_dir = work / ".backup"
            backups = sorted(backup_dir.iterdir())
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), original_text)

    def test_eqn2dmath_eqnum_reverse_fixture_overwrite_matches_expected_output_and_creates_backup(self) -> None:
        """Reverse numbered-equation conversion overwrites and backs up fixtures."""

        fixture_dir = FIXTURES_ROOT / "eqn2dmath-eqnum" / "reverse"
        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            copied_input, original_text, expected_text = self._copy_fixture_input(fixture_dir, work)

            result = self.run_cli("eqn2dmath_eqnum", str(copied_input), "--reverse")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(copied_input.read_text(encoding="utf-8"), expected_text)
            backup_dir = work / ".backup"
            backups = sorted(backup_dir.iterdir())
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), original_text)

    def test_dmath_eqnum2eqn_fixture_overwrite_matches_expected_output_and_creates_backup(self) -> None:
        """The dmath-eqnum2eqn alias rewrites eqnum display math with backups."""

        fixture_dir = FIXTURES_ROOT / "eqn2dmath-eqnum" / "reverse"
        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            copied_input, original_text, expected_text = self._copy_fixture_input(fixture_dir, work)

            result = self.run_cli("dmath_eqnum2eqn", str(copied_input))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(copied_input.read_text(encoding="utf-8"), expected_text)
            backup_dir = work / ".backup"
            backups = sorted(backup_dir.iterdir())
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), original_text)

    def test_eqn2dmath_eqnum_output_option_uses_expected_output_without_touching_source(self) -> None:
        """Writing numbered-equation output separately preserves the source."""

        fixture_dir = FIXTURES_ROOT / "eqn2dmath-eqnum" / "forward"
        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            copied_input, original_text, expected_text = self._copy_fixture_input(fixture_dir, work)
            output_path = work / "converted.tex"

            result = self.run_cli("eqn2dmath_eqnum", str(copied_input), "-o", str(output_path))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(copied_input.read_text(encoding="utf-8"), original_text)
            self.assertEqual(output_path.read_text(encoding="utf-8"), expected_text)
            self.assertFalse((work / ".backup").exists())
