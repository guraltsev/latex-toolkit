"""Command tests for bracing configured unary macro arguments.

The tests invoke the real CLI command against temporary files and check
user-visible output plus backup side effects. Scanner internals and clipboard
integration are out of scope.
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


class UnaryMacroBracingCommandTests(TestCase):
    def run_cli(self, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        """Run a latex-toolkit command with the checkout source on ``PYTHONPATH``."""

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

    def test_default_macros_overwrite_document_body_and_keep_backup(self) -> None:
        """The default command list braces unary macro arguments in document bodies."""

        source = (
            "\\newcommand\\FT[1]{#1}\n"
            "\\begin{document}\n"
            "\\FT f + \\bar x + \\tilde\\alpha + \\dot{x} + \\hat y\n"
            "% \\bar z\n"
            "\\end{document}\n"
        )
        expected = (
            "\\newcommand\\FT[1]{#1}\n"
            "\\begin{document}\n"
            "\\FT{f} + \\bar{x} + \\tilde{\\alpha} + \\dot{x} + \\hat{y}\n"
            "% \\bar z\n"
            "\\end{document}\n"
        )

        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            input_path = work / "paper.tex"
            input_path.write_text(source, encoding="utf-8")

            result = self.run_cli("brace_unary_macros", str(input_path))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(input_path.read_text(encoding="utf-8"), expected)
            backups = sorted((work / ".backup").iterdir())
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), source)

    def test_absolute_toml_replaces_default_macro_list(self) -> None:
        """An absolute TOML command list controls which macros are braced."""

        source = "\\foo x + \\bar y\n"
        expected = "\\foo{x} + \\bar y\n"

        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            input_path = work / "paper.tex"
            output_path = work / "paper.converted.tex"
            macros_path = work / "macros.toml"
            input_path.write_text(source, encoding="utf-8")
            macros_path.write_text("commands = ['\\foo']\n", encoding="utf-8")

            result = self.run_cli(
                "brace_unary_macros",
                str(input_path),
                "--macros-file",
                str(macros_path),
                "--output-file",
                str(output_path),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(input_path.read_text(encoding="utf-8"), source)
            self.assertEqual(output_path.read_text(encoding="utf-8"), expected)
            self.assertFalse((work / ".backup").exists())

    def test_macros_file_path_must_be_absolute(self) -> None:
        """A relative TOML command list path is rejected before rewriting files."""

        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            input_path = work / "paper.tex"
            input_path.write_text("\\foo x\n", encoding="utf-8")
            (work / "macros.toml").write_text("commands = ['\\foo']\n", encoding="utf-8")

            result = self.run_cli(
                "brace_unary_macros",
                str(input_path),
                "--macros-file",
                "macros.toml",
                cwd=work,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("must be absolute", result.stderr)
            self.assertEqual(input_path.read_text(encoding="utf-8"), "\\foo x\n")
