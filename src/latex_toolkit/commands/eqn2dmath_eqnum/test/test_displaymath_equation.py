"""Command transform tests for display-math and equation conversions.

The tests call command public text transforms and assert observable LaTeX
rewrites. CLI backup behavior and parser implementation details are out of
scope.
"""

from __future__ import annotations

from unittest import TestCase

import test_support  # noqa: F401

from latex_toolkit.commands.eqn2dmath_eqnum.main import transform_text as convert_eqn_eqnum_text  # noqa: E402
from latex_toolkit.commands.eqn_star2dmath.main import transform_text as convert_eqn_star_text  # noqa: E402


class EquationDisplayMathTransformTests(TestCase):
    def test_equation_star_forward_only_rewrites_document_body_and_preserves_eqnum_displaymath(self) -> None:
        """Forward equation* conversion rewrites document-body environments only."""

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
        """Reverse equation* conversion leaves standalone eqnum display math alone."""

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
        """Numbered equation conversion preserves leading body whitespace."""

        source = "\\begin{document}\\begin{equation}\n  x+y\n\\end{equation}\\end{document}"

        converted = convert_eqn_eqnum_text(source)

        self.assertEqual(converted, "\\begin{document}\\[\\eqnum\n  x+y\n\\]\\end{document}")

    def test_eqnum_displaymath_reverse_only_rewrites_standalone_eqnum_prefix(self) -> None:
        """Eqnum reverse conversion rewrites only standalone eqnum prefixes."""

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
