r"""Library tests for ``\tmscript`` to ``\substack`` conversion.

The tests call the public text conversion function and assert observable LaTeX
rewrites. CLI write policy and low-level tokenizer spans are out of scope.
"""

from __future__ import annotations

from pathlib import Path
from unittest import TestCase
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from latex_toolkit.lib.tmscript_substack import convert_text  # noqa: E402


class TmscriptSubstackLibraryTests(TestCase):
    def test_centered_tmscript_array_is_rewritten_in_document_body(self) -> None:
        """Centered TeXmacs script arrays become substacks in document bodies."""

        source = (
            "\\documentclass{article}\n"
            "\\newcommand{\\keep}{\\tmscript{\\begin{array}{c}p\\end{array}}}\n"
            "\\begin{document}\n"
            "A \\tmscript{\\begin{array}{c}i\\\\j\\end{array}} B\n"
            "% \\tmscript{\\begin{array}{c}ignored\\end{array}}\n"
            "\\end{document}\n"
            "\\tmscript{\\begin{array}{c}tail\\end{array}}\n"
        )

        converted = convert_text(source)

        self.assertEqual(
            converted,
            "\\documentclass{article}\n"
            "\\newcommand{\\keep}{\\tmscript{\\begin{array}{c}p\\end{array}}}\n"
            "\\begin{document}\n"
            "A \\substack{i\\\\j} B\n"
            "% \\tmscript{\\begin{array}{c}ignored\\end{array}}\n"
            "\\end{document}\n"
            "\\tmscript{\\begin{array}{c}tail\\end{array}}\n",
        )

    def test_only_centered_single_column_array_arguments_are_rewritten(self) -> None:
        """Non-centered arrays and extra argument content are preserved."""

        source = (
            "\\tmscript{\\begin{array}{l}i\\\\j\\end{array}}\n"
            "\\tmscript{\\begin{array}{c}i\\end{array}x}\n"
            "\\tmscript{x}\n"
        )

        converted = convert_text(source)

        self.assertEqual(converted, source)
