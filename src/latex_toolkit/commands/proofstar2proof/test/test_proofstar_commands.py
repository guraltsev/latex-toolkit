"""Command tests for titled ``proof*`` and ``proof`` conversion.

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


class ProofstarCommandTests(TestCase):
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

    def test_proofstar2proof_overwrites_with_expected_output_and_backup(self) -> None:
        """The command overwrites converted files and keeps a backup."""

        source = "\\begin{proof*}{POOF}\n  strs\n\\end{proof*}\n"
        expected = "\\begin{proof}[POOF]\nstrs\n\\end{proof}\n"

        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            input_path = work / "proof.tex"
            input_path.write_text(source, encoding="utf-8")

            result = self.run_cli("proofstar2proof", str(input_path))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(input_path.read_text(encoding="utf-8"), expected)
            backups = sorted((work / ".backup").iterdir())
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), source)

    def test_proofstar2proof_reverse_overwrites_with_expected_output_and_backup(self) -> None:
        """The reverse option overwrites converted files and keeps a backup."""

        source = "\\begin{proof}[POOF]\nstrs\n\\end{proof}\n"
        expected = "\\begin{proof*}{POOF}\nstrs\n\\end{proof*}\n"

        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            input_path = work / "proof.tex"
            input_path.write_text(source, encoding="utf-8")

            result = self.run_cli("proofstar2proof", str(input_path), "--reverse")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(input_path.read_text(encoding="utf-8"), expected)
            backups = sorted((work / ".backup").iterdir())
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), source)

    def test_proof2proofstar_alias_overwrites_with_expected_output_and_backup(self) -> None:
        """The inverse command rewrites titled proof environments to proofstar."""

        source = "\\begin{proof}[POOF]\nstrs\n\\end{proof}\n"
        expected = "\\begin{proof*}{POOF}\nstrs\n\\end{proof*}\n"

        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            input_path = work / "proof.tex"
            input_path.write_text(source, encoding="utf-8")

            result = self.run_cli("proof2proofstar", str(input_path))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(input_path.read_text(encoding="utf-8"), expected)
            backups = sorted((work / ".backup").iterdir())
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), source)
