"""Command tests for dollar and bracket math delimiter conversion.

The tests invoke real CLI commands against temporary files and check
user-visible output files plus backup side effects. Clipboard integration and
parser internals are out of scope.
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


class DollarDelimiterCommandTests(TestCase):
    def run_cli(self, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        command_name, *command_args = args
        env = os.environ.copy()
        env["PYTHONPATH"] = str(SRC)
        return subprocess.run(
            [sys.executable, "-m", f"latex-toolkit.commands.{command_name}", *command_args],
            cwd=str(cwd) if cwd is not None else None,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_dollar2bracket_overwrites_with_expected_output_and_backup(self) -> None:
        """Forward delimiter conversion overwrites files and backs up originals."""

        source = "$x$ and $$y$$\n"
        expected = "\\(x\\) and \\[y\\]\n"
        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            input_path = work / "math.tex"
            input_path.write_text(source, encoding="utf-8")

            result = self.run_cli("dollar2bracket", str(input_path))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(input_path.read_text(encoding="utf-8"), expected)
            backups = sorted((work / ".backup").iterdir())
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), source)

    def test_bracket2dollar_overwrites_with_expected_output_and_backup(self) -> None:
        """Reverse delimiter conversion is available as a command alias."""

        source = "\\(x\\) and \\[y\\]\n"
        expected = "$x$ and $$y$$\n"
        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            input_path = work / "math.tex"
            input_path.write_text(source, encoding="utf-8")

            result = self.run_cli("bracket2dollar", str(input_path))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(input_path.read_text(encoding="utf-8"), expected)
            backups = sorted((work / ".backup").iterdir())
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), source)
