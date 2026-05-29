"""Command tests for singular named-reference cleveref rewrites.

The tests invoke the real CLI command against temporary files and check
user-visible output plus backup side effects. Scanner internals and clipboard
integration are out of scope.
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
import subprocess
import sys

from test_support import pythonpath_env


class RefToCrefCommandTests(TestCase):
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

    def test_ref_to_cref_overwrites_with_expected_output_and_backup(self) -> None:
        """The command overwrites rewritten files and keeps a backup."""

        source = (
            "Proposition~\\ref{prop:main}\n"
            "lemma \\ref{lemma:minor}\n"
            "Remark \\ref{remark:stay}\n"
        )
        expected = (
            "\\Cref{prop:main}\n"
            "\\cref{lemma:minor}\n"
            "Remark \\ref{remark:stay}\n"
        )

        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            input_path = work / "paper.tex"
            input_path.write_text(source, encoding="utf-8")

            result = self.run_cli("ref_to_cref", str(input_path))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(input_path.read_text(encoding="utf-8"), expected)
            backups = sorted((work / ".backup").iterdir())
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), source)
