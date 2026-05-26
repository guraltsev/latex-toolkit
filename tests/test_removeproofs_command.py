"""Tests for removing proof environments from LaTeX text.

The tests exercise the public command entrypoint with clipboard I/O mocked and
the parser boundary faked. File layout, parser internals, and real network
installation are out of scope.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from latex_toolkit.commands.removeproofs import main as removeproofs_command  # noqa: E402


class RemoveProofsCommandTests(TestCase):
    def test_missing_dependency_triggers_install_before_transform(self) -> None:
        """The command installs ``pylatexenc`` when the dependency is missing."""

        class FakeLatexWalker:
            def __init__(self, text: str) -> None:
                self.text = text

            def get_latex_nodes(self):
                start = self.text.index(r"\begin{proof}")
                end = self.text.index(r"\end{proof}") + len(r"\end{proof}")
                node = SimpleNamespace(
                    pos=start,
                    pos_end=end,
                    environmentname="proof",
                    nodelist=None,
                    nodeargd=None,
                )
                return [node], 0, len(self.text)

        source = "Keep\n\\begin{proof}Drop\\end{proof}\nDone\n"

        with (
            patch(
                "latex_toolkit.commands.removeproofs.main.importlib.util.find_spec",
                side_effect=[None, object()],
            ),
            patch("latex_toolkit.commands.removeproofs.main.subprocess.run") as run,
            patch(
                "latex_toolkit.commands.removeproofs.main._load_latexwalker",
                return_value=FakeLatexWalker,
            ),
        ):
            run.return_value = removeproofs_command.subprocess.CompletedProcess(
                args=[], returncode=0, stdout="", stderr=""
            )
            converted = removeproofs_command.transform_text(source)

        self.assertEqual(converted, "Keep\n\nDone\n")
        self.assertEqual(run.call_count, 1)
        self.assertIn("pylatexenc", run.call_args.args[0])
        self.assertIn("--target", run.call_args.args[0])

    def test_clipboard_is_default_mode_without_input_paths(self) -> None:
        """Running the command with no arguments transforms clipboard text."""

        class FakeLatexWalker:
            def __init__(self, text: str) -> None:
                self.text = text

            def get_latex_nodes(self):
                start = self.text.index(r"\begin{proof}")
                end = self.text.index(r"\end{proof}") + len(r"\end{proof}")
                node = SimpleNamespace(
                    pos=start,
                    pos_end=end,
                    environmentname="proof",
                    nodelist=None,
                    nodeargd=None,
                )
                return [node], 0, len(self.text)

        with (
            patch("latex_toolkit.commands.removeproofs.main.ensure_pylatexenc"),
            patch(
                "latex_toolkit.commands.removeproofs.main._load_latexwalker",
                return_value=FakeLatexWalker,
            ),
            patch("latex_toolkit.lib.clipboard.pyperclip.paste", return_value="Keep\n\\begin{proof}Drop\\end{proof}\nDone\n"),
            patch("latex_toolkit.lib.clipboard.pyperclip.copy") as copy,
        ):
            result = removeproofs_command.main([])

        self.assertEqual(result, 0)
        copy.assert_called_once_with("Keep\n\nDone\n")
