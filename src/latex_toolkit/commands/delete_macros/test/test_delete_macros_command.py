"""Command tests for deleting configured unary macro calls.

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


class DeleteMacrosCommandTests(TestCase):
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

    def test_default_macros_remove_hyphenated_wrapper_calls_and_keep_backup(self) -> None:
        """The default delete list removes ``\\hide-preamble`` calls and preserves backups."""

        source = (
            "\\begin{document}\n"
            "\\hide-preamble{\\usepackage{foo}}\n"
            "\\section{Body}\n"
            "% \\hide-preamble{comment}\n"
            "\\end{document}\n"
        )
        expected = (
            "\\begin{document}\n"
            "\n"
            "\\section{Body}\n"
            "% \\hide-preamble{comment}\n"
            "\\end{document}\n"
        )

        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            input_path = work / "paper.tex"
            input_path.write_text(source, encoding="utf-8")

            result = self.run_cli("delete_macros", str(input_path))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(input_path.read_text(encoding="utf-8"), expected)
            backups = sorted((work / ".backup").iterdir())
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), source)

    def test_absolute_toml_replaces_default_macro_list(self) -> None:
        """An absolute TOML command list controls which unary macro calls are deleted."""

        source = "\\drop-me{A} + \\hide-preamble{B}\n"
        expected = " + \\hide-preamble{B}\n"

        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            input_path = work / "paper.tex"
            output_path = work / "paper.converted.tex"
            macros_path = work / "macros.toml"
            input_path.write_text(source, encoding="utf-8")
            macros_path.write_text("commands = ['\\drop-me']\n", encoding="utf-8")

            result = self.run_cli(
                "delete_macros",
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
            input_path.write_text("\\hide-preamble{A}\n", encoding="utf-8")
            (work / "macros.toml").write_text("commands = ['\\drop-me']\n", encoding="utf-8")

            result = self.run_cli(
                "delete_macros",
                str(input_path),
                "--macros-file",
                "macros.toml",
                cwd=work,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("must be absolute", result.stderr)
            self.assertEqual(input_path.read_text(encoding="utf-8"), "\\hide-preamble{A}\n")
