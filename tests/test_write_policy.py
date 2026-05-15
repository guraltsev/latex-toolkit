"""Tests for observable command write and clipboard behavior.

The tests exercise public command behavior through real CLI invocations or the
public command entrypoint with the system clipboard boundary mocked. Parser
internals, import choices, source layout, and package metadata are out of
scope.
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from latex_toolkit.commands.strip_comments import main as strip_comments_command  # noqa: E402


def _pythonpath_env() -> dict[str, str]:
    """Return an environment that imports package modules from ``src``."""

    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC)
    return env


class ObservableWritePolicyTests(TestCase):
    def run_cli(self, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        """Run a public command package with source-checkout imports."""

        command_name, *command_args = args
        return subprocess.run(
            [sys.executable, "-m", f"latex_toolkit.commands.{command_name}", *command_args],
            cwd=str(cwd) if cwd is not None else None,
            env=_pythonpath_env(),
            text=True,
            capture_output=True,
            check=False,
        )

    def test_default_file_mode_overwrites_input_and_keeps_backup(self) -> None:
        """Default file mode replaces the input file and saves its original contents."""

        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            source = work / "paper.tex"
            original = "keep \\% literal % drop me\n"
            source.write_text(original, encoding="utf-8")

            result = self.run_cli("strip_comments", str(source))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(source.read_text(encoding="utf-8"), "keep \\% literal \n")
            backups = sorted((work / ".backup").iterdir())
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), original)

    def test_output_aliases_preserve_input_and_skip_backup(self) -> None:
        """Each documented output spelling writes elsewhere without backing up."""

        for option in ("-o", "--output", "--output-file"):
            with self.subTest(option=option), TemporaryDirectory() as temp_dir:
                work = Path(temp_dir)
                source = work / "paper.tex"
                output = work / "clean.tex"
                original = "keep % drop me\n"
                source.write_text(original, encoding="utf-8")

                result = self.run_cli("strip_comments", str(source), option, str(output))

                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(source.read_text(encoding="utf-8"), original)
                self.assertEqual(output.read_text(encoding="utf-8"), "keep \n")
                self.assertFalse((work / ".backup").exists())

    def test_no_backup_overwrites_without_creating_backup_directory(self) -> None:
        """The no-backup option leaves only the rewritten source file behind."""

        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            source = work / "paper.tex"
            source.write_text("keep % drop me\n", encoding="utf-8")

            result = self.run_cli("strip_comments", str(source), "-B")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(source.read_text(encoding="utf-8"), "keep \n")
            self.assertFalse((work / ".backup").exists())

    def test_clipboard_mode_replaces_clipboard_text_without_files(self) -> None:
        """Clipboard mode transforms clipboard text through the clipboard boundary."""

        with (
            patch("latex_toolkit.lib.clipboard.pyperclip.paste", return_value="keep % drop me\n"),
            patch("latex_toolkit.lib.clipboard.pyperclip.copy") as copy,
        ):
            result = strip_comments_command.main(["--clipboard"])

        self.assertEqual(result, 0)
        copy.assert_called_once_with("keep \n")

    def test_clipboard_mode_rejects_input_paths_with_parser_error(self) -> None:
        """Clipboard mode reports a concise parser error when combined with a file."""

        result = self.run_cli("strip_comments", "--clipboard", "paper.tex")

        self.assertEqual(result.returncode, 2)
        self.assertIn("--clipboard cannot be combined with input or output paths.", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
