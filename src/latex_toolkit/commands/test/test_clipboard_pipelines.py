"""Tests for observable clipboard pipeline behavior.

The tests mock the system clipboard boundary while running public pipeline
entrypoints or the public pipeline runner. Individual transform internals,
source layout, and batch-file contents are out of scope.
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
import sys

from test_support import SRC_ROOT

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from latex_toolkit.commands.llm_latex_to_texmacs_latex import main as llm_to_texmacs_command  # noqa: E402
from latex_toolkit.commands.texmacs_latex_to_latex import main as texmacs_to_latex_command  # noqa: E402
from latex_toolkit.commands.texmacs_latex_to_llm_latex import main as texmacs_to_llm_command  # noqa: E402
from latex_toolkit.commands.tm2tm import main as tm2tm_command  # noqa: E402
from latex_toolkit.lib.logging_config import run_clipboard_pipeline  # noqa: E402


class ClipboardPipelineTests(TestCase):
    def test_texmacs_to_llm_pipeline_replaces_clipboard_with_ordered_output(self) -> None:
        """The TeXmacs-to-LLM pipeline applies every conversion to clipboard text."""

        source = (
            "$\u03b1$\n"
            "\\begin{ltae}x\\\\y\\end{ltae}\n"
            "\\tmscript{\\begin{array}{c}i\\\\j\\end{array}}\n"
            "\\begin{proof*}{Idea}Done.\\end{proof*}\n"
        )
        expected = (
            "\\(\\alpha \\)\n"
            "\\begin{aligned}[t]&x\\\\&y\\end{aligned}\n"
            "\\substack{i\\\\j}\n"
            "\\begin{proof}[Idea]Done.\\end{proof}\n"
        )
        writes: list[str] = []

        with (
            patch("latex_toolkit.lib.clipboard.pyperclip.paste", return_value=source),
            patch("latex_toolkit.lib.clipboard.pyperclip.copy", side_effect=writes.append),
        ):
            result = texmacs_to_llm_command.main([])

        self.assertEqual(result, 0)
        self.assertEqual(writes[-1], expected)

    def test_llm_to_texmacs_pipeline_replaces_clipboard_with_ordered_output(self) -> None:
        """The LLM-to-TeXmacs pipeline applies bracing, delimiter, and proof rewrites."""

        source = "\\bar x + \\left\\|v\\right\\|\n\\begin{proof}[Idea]Done.\\end{proof}\n"
        expected = "\\bar{x} + \\left \\lVert v\\right \\rVert\n\\begin{proof*}{Idea}Done.\\end{proof*}\n"
        writes: list[str] = []

        with (
            patch("latex_toolkit.lib.clipboard.pyperclip.paste", return_value=source),
            patch("latex_toolkit.lib.clipboard.pyperclip.copy", side_effect=writes.append),
        ):
            result = llm_to_texmacs_command.main([])

        self.assertEqual(result, 0)
        self.assertEqual(writes[-1], expected)

    def test_llm_to_texmacs_macros_file_controls_bracing_step(self) -> None:
        """A custom macro file changes the first pipeline step's visible output."""

        with TemporaryDirectory() as temp_dir:
            macros_file = Path(temp_dir) / "macros.toml"
            macros_file.write_text(r"commands = ['\foo']" + "\n", encoding="utf-8")
            writes: list[str] = []

            with (
                patch("latex_toolkit.lib.clipboard.pyperclip.paste", return_value="\\foo x + \\bar y\n"),
                patch("latex_toolkit.lib.clipboard.pyperclip.copy", side_effect=writes.append),
            ):
                result = llm_to_texmacs_command.main(["--macros-file", str(macros_file)])

        self.assertEqual(result, 0)
        self.assertEqual(writes[-1], "\\foo{x} + \\bar y\n")

    def test_llm_to_texmacs_rejects_ambiguous_macro_arguments(self) -> None:
        """Passing both macro-file spellings reports a parser error."""

        with self.assertRaises(SystemExit) as error:
            llm_to_texmacs_command.main(["--macros-file", "C:\\macros.toml", "C:\\other.toml"])

        self.assertEqual(error.exception.code, 2)

    def test_llm_to_texmacs_invalid_macros_file_leaves_clipboard_unchanged(self) -> None:
        """Invalid macro configuration fails before the clipboard is replaced."""

        with (
            patch("latex_toolkit.lib.clipboard.pyperclip.paste") as paste,
            patch("latex_toolkit.lib.clipboard.pyperclip.copy") as copy,
        ):
            result = llm_to_texmacs_command.main(["--macros-file", "relative.toml"])

        self.assertEqual(result, 1)
        paste.assert_not_called()
        copy.assert_not_called()

    def test_texmacs_to_latex_pipeline_deletes_default_macros_after_normalization(self) -> None:
        """The TeXmacs-to-LaTeX pipeline applies the base steps and then deletes wrappers."""

        source = (
            "\\hide-preamble{\\usepackage{foo}}\n"
            "$\\alpha$\n"
            "\\begin{proof*}{Idea}Done.\\end{proof*}\n"
        )
        expected = "\n\\(\\alpha\\)\n\\begin{proof}[Idea]Done.\\end{proof}\n"
        writes: list[str] = []

        with (
            patch("latex_toolkit.lib.clipboard.pyperclip.paste", return_value=source),
            patch("latex_toolkit.lib.clipboard.pyperclip.copy", side_effect=writes.append),
        ):
            result = texmacs_to_latex_command.main([])

        self.assertEqual(result, 0)
        self.assertEqual(writes[-1], expected)

    def test_texmacs_to_latex_macros_file_controls_delete_step(self) -> None:
        """A custom macro file changes which final delete step rewrites are visible."""

        with TemporaryDirectory() as temp_dir:
            macros_file = Path(temp_dir) / "macros.toml"
            macros_file.write_text("commands = ['\\drop-me']\n", encoding="utf-8")
            writes: list[str] = []

            with (
                patch(
                    "latex_toolkit.lib.clipboard.pyperclip.paste",
                    return_value="\\drop-me{A}\n\\hide-preamble{B}\n",
                ),
                patch("latex_toolkit.lib.clipboard.pyperclip.copy", side_effect=writes.append),
            ):
                result = texmacs_to_latex_command.main(["--macros-file", str(macros_file)])

        self.assertEqual(result, 0)
        self.assertEqual(writes[-1], "\n\\hide-preamble{B}\n")

    def test_tm2tm_pipeline_replaces_clipboard_with_texmacs_normalization(self) -> None:
        """The TeXmacs snippet pipeline normalizes strict aligned tables."""

        source = "<aligned|t|<tformat|<table|<row|<cell|>|<cell|x>>>>>\n"
        writes: list[str] = []

        with (
            patch("latex_toolkit.lib.clipboard.pyperclip.paste", return_value=source),
            patch("latex_toolkit.lib.clipboard.pyperclip.copy", side_effect=writes.append),
        ):
            result = tm2tm_command.main([])

        self.assertEqual(result, 0)
        self.assertEqual(writes[-1], "<ltae|<tformat|<table|<row|<cell|x>>>>>\n")

    def test_pipeline_runner_stops_after_failure_and_keeps_successful_writes(self) -> None:
        """A failing step stops later steps while preserving earlier clipboard updates."""

        def fail_step(_: str) -> str:
            raise RuntimeError("boom")

        writes: list[str] = []

        with (
            patch("latex_toolkit.lib.clipboard.pyperclip.paste", return_value="seed"),
            patch("latex_toolkit.lib.clipboard.pyperclip.copy", side_effect=writes.append),
        ):
            with self.assertRaisesRegex(RuntimeError, "fail failed: boom"):
                run_clipboard_pipeline(
                    "demo",
                    (
                        ("first", lambda text: f"{text} first"),
                        ("fail", fail_step),
                        ("later", lambda text: f"{text} later"),
                    ),
                )

        self.assertEqual(writes, ["seed first"])
