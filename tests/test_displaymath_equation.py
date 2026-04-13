from __future__ import annotations

from pathlib import Path
from unittest import TestCase
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lib.equation_eqnum_displaymath import convert_text as convert_eqn_eqnum_text  # noqa: E402
from lib.equation_star_displaymath import convert_text as convert_eqn_star_text  # noqa: E402


class EquationDisplayMathLibraryTests(TestCase):
    def test_equation_star_forward_only_rewrites_document_body_and_preserves_eqnum_displaymath(self) -> None:
        source = (
            "\\documentclass{article}\n"
            "\\newcommand{\\keep}{\\begin{equation*}p\\end{equation*}}\n"
            "\\begin{document}\n"
            "A \\begin{equation*}x\\end{equation*}alpha\n"
            "\\[\\eqnum y\\]\n"
            "% \\begin{equation*}ignored\\end{equation*}\n"
            "\\end{document}\n"
            "\\begin{equation*}tail\\end{equation*}\n"
        )

        converted = convert_eqn_star_text(source)

        self.assertEqual(
            converted,
            "\\documentclass{article}\n"
            "\\newcommand{\\keep}{\\begin{equation*}p\\end{equation*}}\n"
            "\\begin{document}\n"
            "A \\[x\\]alpha\n"
            "\\[\\eqnum y\\]\n"
            "% \\begin{equation*}ignored\\end{equation*}\n"
            "\\end{document}\n"
            "\\begin{equation*}tail\\end{equation*}\n",
        )

    def test_equation_star_reverse_skips_standalone_eqnum_blocks(self) -> None:
        source = (
            "\\begin{document}\n"
            "\\[x\\]\n"
            "\\[\\eqnum y\\]\n"
            "\\[\\eqnumber z\\]\n"
            "% \\[ignored\\]\n"
            "\\end{document}\n"
        )

        converted = convert_eqn_star_text(source, reverse=True)

        self.assertEqual(
            converted,
            "\\begin{document}\n"
            "\\begin{equation*}x\\end{equation*}\n"
            "\\[\\eqnum y\\]\n"
            "\\begin{equation*}\\eqnumber z\\end{equation*}\n"
            "% \\[ignored\\]\n"
            "\\end{document}\n",
        )

    def test_equation_forward_inserts_eqnum_without_double_spacing_before_leading_whitespace(self) -> None:
        source = "\\begin{document}\\begin{equation}\n  x+y\n\\end{equation}\\end{document}"

        converted = convert_eqn_eqnum_text(source)

        self.assertEqual(converted, "\\begin{document}\\[\\eqnum\n  x+y\n\\]\\end{document}")

    def test_eqnum_displaymath_reverse_only_rewrites_standalone_eqnum_prefix(self) -> None:
        source = (
            "\\begin{document}\n"
            "\\[\\eqnum x\\]\n"
            "\\[plain\\]\n"
            "\\[\\eqnumber y\\]\n"
            "% \\[\\eqnum ignored\\]\n"
            "\\end{document}\n"
        )

        converted = convert_eqn_eqnum_text(source, reverse=True)

        self.assertEqual(
            converted,
            "\\begin{document}\n"
            "\\begin{equation} x\\end{equation}\n"
            "\\[plain\\]\n"
            "\\[\\eqnumber y\\]\n"
            "% \\[\\eqnum ignored\\]\n"
            "\\end{document}\n",
        )
