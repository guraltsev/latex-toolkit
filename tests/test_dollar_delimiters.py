"""Library tests for dollar and bracket math delimiter conversion.

The tests call the public text conversion function and assert observable
LaTeX rewrites. Tokenization internals are out of scope.
"""

from __future__ import annotations

from pathlib import Path
from unittest import TestCase
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
TOOLKIT = SRC / "latex-toolkit"
if str(TOOLKIT) not in sys.path:
    sys.path.insert(0, str(TOOLKIT))

from lib.dollar_delimiters import convert_text  # noqa: E402


class DollarDelimiterTests(TestCase):
    def test_dollar_delimiters_convert_only_matched_document_body_pairs(self) -> None:
        """Dollar conversion preserves preamble, comments, escapes, and unmatched delimiters."""

        source = (
            "\\documentclass{article}\n"
            "\\newcommand{\\keep}{$p$}\n"
            "\\begin{document}\n"
            "Inline $x$ and display $$y$$.\n"
            "Escaped \\$ price and unmatched $ stays.\n"
            "% $ ignored and $$ ignored\n"
            "\\end{document}\n"
            "$tail$\n"
        )

        converted = convert_text(source)

        self.assertEqual(
            converted,
            "\\documentclass{article}\n"
            "\\newcommand{\\keep}{$p$}\n"
            "\\begin{document}\n"
            "Inline \\(x\\) and display \\[y\\].\n"
            "Escaped \\$ price and unmatched $ stays.\n"
            "% $ ignored and $$ ignored\n"
            "\\end{document}\n"
            "$tail$\n",
        )

    def test_bracket_delimiters_convert_only_matched_document_body_pairs(self) -> None:
        """Reverse conversion preserves linebreak options and unmatched delimiters."""

        source = (
            "\\documentclass{article}\n"
            "\\newcommand{\\keep}{\\(p\\)}\n"
            "\\begin{document}\n"
            "Inline \\(x\\) and display \\[y\\].\n"
            "Row break \\\\[0.5em]\n"
            "Unmatched \\[ stays.\n"
            "% \\(ignored\\)\n"
            "\\end{document}\n"
            "\\[tail\\]\n"
        )

        converted = convert_text(source, reverse=True)

        self.assertEqual(
            converted,
            "\\documentclass{article}\n"
            "\\newcommand{\\keep}{\\(p\\)}\n"
            "\\begin{document}\n"
            "Inline $x$ and display $$y$$.\n"
            "Row break \\\\[0.5em]\n"
            "Unmatched \\[ stays.\n"
            "% \\(ignored\\)\n"
            "\\end{document}\n"
            "\\[tail\\]\n",
        )
