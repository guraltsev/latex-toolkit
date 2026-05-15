r"""Command tests for TeXmacs vertical delimiter normalization.

The tests invoke the real CLI command against a temporary file and check
user-visible output plus backup side effects. Clipboard integration and regex
implementation details are out of scope.
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


class TexmacsVertDelimiterCommandTests(TestCase):
    def run_cli(self, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        """Run a latex-toolkit command with the checkout source on ``PYTHONPATH``."""

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

    def test_sized_double_bar_delimiters_rewrite_for_texmacs(self) -> None:
        """The command rewrites sized double-bar delimiters in document bodies."""

        source = (
            "\\newcommand{\\normbars}[1]{\\left\\| #1 \\right\\|}\n"
            "\\begin{document}\n"
            "$\\left\\|x\\right\\| + \\Bigl\\|y\\Bigr\\| + "
            "\\biggl\\|\\frac{a}{b}\\biggr\\| + \\middle\\| + \\bigm\\|$\n"
            "% \\left\\|comment\\right\\|\n"
            "\\end{document}\n"
        )
        expected = (
            "\\newcommand{\\normbars}[1]{\\left\\| #1 \\right\\|}\n"
            "\\begin{document}\n"
            "$\\left \\lVert x\\right \\rVert + \\Bigl \\lVert y\\Bigr \\rVert + "
            "\\biggl \\lVert\\frac{a}{b}\\biggr \\rVert + \\middle \\Vert + \\bigm \\Vert$\n"
            "% \\left\\|comment\\right\\|\n"
            "\\end{document}\n"
        )

        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            input_path = work / "paper.tex"
            input_path.write_text(source, encoding="utf-8")

            result = self.run_cli("texmacs_vert_delimiters", str(input_path))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(input_path.read_text(encoding="utf-8"), expected)
            backups = sorted((work / ".backup").iterdir())
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), source)
