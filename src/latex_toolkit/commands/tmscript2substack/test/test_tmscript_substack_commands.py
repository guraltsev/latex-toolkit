r"""Command tests for ``\tmscript`` to ``\substack`` conversion.

The tests invoke the real CLI command against a temporary file and check
user-visible output plus backup side effects. Parser implementation details are
out of scope.
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
import subprocess
import sys

from test_support import pythonpath_env


class TmscriptSubstackCommandTests(TestCase):
    def run_cli(self, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        """Run a latex-toolkit command with the checkout source on ``PYTHONPATH``."""

        command_name, *command_args = args
        return subprocess.run(
            [sys.executable, "-m", f"latex_toolkit.commands.{command_name}", *command_args],
            cwd=str(cwd) if cwd is not None else None,
            env=pythonpath_env(),
            text=True,
            capture_output=True,
            check=False,
        )

    def test_tmscript2substack_overwrites_with_expected_output_and_backup(self) -> None:
        """The command overwrites converted files and keeps a backup."""

        source = "x_{\\tmscript{\\begin{array}{c}i\\\\j\\end{array}}}\n"
        expected = "x_{\\substack{i\\\\j}}\n"

        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            input_path = work / "script.tex"
            input_path.write_text(source, encoding="utf-8")

            result = self.run_cli("tmscript2substack", str(input_path))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(input_path.read_text(encoding="utf-8"), expected)
            backups = sorted((work / ".backup").iterdir())
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), source)
