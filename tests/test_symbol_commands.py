"""Command tests for LaTeX/Unicode symbol conversion.

The tests invoke real CLI commands against fixture files and check observable
file contents plus backup side effects. The exact tokenization internals are
out of scope.
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
FIXTURES = ROOT / "tests" / "fixtures"


class SymbolCommandTests(TestCase):
    def run_cli(self, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        command_name, *command_args = args
        env = os.environ.copy()
        env["PYTHONPATH"] = str(SRC)
        return subprocess.run(
            [sys.executable, "-m", f"latex_toolkit.commands.{command_name}", *command_args],
            cwd=str(cwd) if cwd is not None else None,
            env=env,
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

    def test_tex2uni_fixture_overwrite_matches_expected_output_and_creates_backup(self) -> None:
        """Forward symbol conversion overwrites fixtures and backs up originals."""

        fixture_dir = FIXTURES / "tex2uni" / "forward"
        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            copied_input, original_text, expected_text = self._copy_fixture_input(fixture_dir, work)

            result = self.run_cli("tex2uni", str(copied_input))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(copied_input.read_text(encoding="utf-8"), expected_text)
            backup_dir = work / ".backup"
            backups = sorted(backup_dir.iterdir())
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), original_text)

    def test_tex2uni_reverse_fixture_overwrite_matches_expected_output_and_creates_backup(self) -> None:
        """Reverse symbol conversion overwrites fixtures and backs up originals."""

        fixture_dir = FIXTURES / "tex2uni" / "reverse"
        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            copied_input, original_text, expected_text = self._copy_fixture_input(fixture_dir, work)

            result = self.run_cli("tex2uni", str(copied_input), "--reverse")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(copied_input.read_text(encoding="utf-8"), expected_text)
            backup_dir = work / ".backup"
            backups = sorted(backup_dir.iterdir())
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), original_text)

    def test_uni2tex_fixture_overwrite_matches_expected_output_and_creates_backup(self) -> None:
        """The uni2tex alias performs reverse conversion with the same write policy."""

        fixture_dir = FIXTURES / "uni2tex" / "basic"
        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            copied_input, original_text, expected_text = self._copy_fixture_input(fixture_dir, work)

            result = self.run_cli("uni2tex", str(copied_input))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(copied_input.read_text(encoding="utf-8"), expected_text)
            backup_dir = work / ".backup"
            backups = sorted(backup_dir.iterdir())
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), original_text)

    def test_uni2tex_preserves_non_ascii_prose_while_converting_math(self) -> None:
        """Unicode prose survives symbol conversion while mapped math changes."""

        source = "Hölder outside and $α$ inside.\n"
        expected = "Hölder outside and $\\alpha $ inside.\n"

        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            input_path = work / "unicode.tex"
            input_path.write_text(source, encoding="utf-8")

            result = self.run_cli("uni2tex", str(input_path))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(input_path.read_text(encoding="utf-8"), expected)

    def test_tex2uni_output_option_uses_expected_output_without_touching_source(self) -> None:
        """Writing converted symbols to an output file preserves the source."""

        fixture_dir = FIXTURES / "tex2uni" / "forward"
        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            copied_input, original_text, expected_text = self._copy_fixture_input(fixture_dir, work)
            output_path = work / "converted.tex"

            result = self.run_cli("tex2uni", str(copied_input), "-o", str(output_path))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(copied_input.read_text(encoding="utf-8"), original_text)
            self.assertEqual(output_path.read_text(encoding="utf-8"), expected_text)
            self.assertFalse((work / ".backup").exists())
