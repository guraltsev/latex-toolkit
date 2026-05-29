"""Tests for removing proof environments from LaTeX text.

The tests exercise the public command entrypoint against real LaTeX input and
real file writes. Parser internals, clipboard stubs, and network scaffolding
are out of scope.
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
import subprocess
import sys

from test_support import REPO_ROOT, pythonpath_env

EXAMPLE = REPO_ROOT / "Discovery" / "remove-proof-test.tex"


def _pythonpath_env() -> dict[str, str]:
    """Return an environment that imports package modules from ``src``."""

    return pythonpath_env()


from latex_toolkit.commands.removeproofs import main as removeproofs_command  # noqa: E402


class RemoveProofsCommandTests(TestCase):
    def test_transform_text_removes_proof_blocks_from_example_content(self) -> None:
        """The public transform removes proof environments from the provided example text."""

        source = EXAMPLE.read_text(encoding="utf-8")
        converted = removeproofs_command.transform_text(source)

        self.assertEqual(converted.count("\\begin{proof}"), 0)
        self.assertEqual(converted.count("\\end{proof}"), 0)
        self.assertIn("\\section{Generalities}", converted)
        self.assertIn("\\begin{itemize}", converted)
        self.assertIn("\\begin{theorem}", converted)

    def test_file_mode_overwrites_input_and_keeps_backup(self) -> None:
        """The command rewrites a file in place and preserves a backup copy."""

        source = EXAMPLE.read_text(encoding="utf-8")

        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            input_path = work / "remove-proof-test.tex"
            input_path.write_text(source, encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "-m", "latex_toolkit.commands.removeproofs", str(input_path)],
                cwd=str(REPO_ROOT),
                env=_pythonpath_env(),
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            converted = input_path.read_text(encoding="utf-8")
            self.assertEqual(converted.count("\\begin{proof}"), 0)
            self.assertEqual(converted.count("\\end{proof}"), 0)
            backups = sorted((work / ".backup").iterdir())
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), source)
