"""Tests for observable manual LaTeX math reformatting behavior.

The tests call the public text transform directly. File writes, backup policy,
and clipboard integration are covered by shared command policy tests; parser
node internals are out of scope.
"""

from __future__ import annotations

from pathlib import Path
import sys
from unittest import TestCase

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from latex_toolkit.commands.manual_latex_reformat.main import transform_text  # noqa: E402


class ManualLatexReformatTests(TestCase):
    def test_display_environment_keeps_boundary_newlines(self) -> None:
        """Display environment bodies keep newlines after begin and before end."""

        source = "\\begin{align}\n  a&=b+c\\\\\n\\end{align}\n"

        transformed = transform_text(source)

        self.assertEqual(
            transformed,
            "\\begin{align}\n"
            "a & =b + c\n"
            "\\\\\n"
            "\\end{align}\n",
        )

    def test_display_environment_preserves_crlf_newline_encoding(self) -> None:
        """Generated formatter newlines use the source CRLF convention."""

        source = "\\begin{align}\r\n  a&=b+c\\\\\r\n\\end{align}\r\n"

        transformed = transform_text(source)

        self.assertEqual(
            transformed,
            "\\begin{align}\r\n"
            "a & =b + c\r\n"
            "\\\\\r\n"
            "\\end{align}\r\n",
        )
        self.assertNotIn("c\n\\\\", transformed)

    def test_equation_label_moves_to_its_own_opening_lines(self) -> None:
        """A leading equation label is kept literal and placed above the body."""

        source = "\\begin{equation}\n\\label{eq:alpha-beta}a+b\n\\end{equation}\n"

        transformed = transform_text(source)

        self.assertEqual(
            transformed,
            "\\begin{equation}\n"
            "\\label{eq:alpha-beta}\n"
            "a + b\n"
            "\\end{equation}\n",
        )

    def test_text_and_mbox_keep_literal_spacing_inside_math(self) -> None:
        """Text-like macro arguments do not get operator spacing inserted."""

        source = (
            "\\begin{equation}\n"
            "a+\\text{A+B-C} + \\mbox{X+Y-Z}\n"
            "\\end{equation}\n"
        )

        transformed = transform_text(source)

        self.assertEqual(
            transformed,
            "\\begin{equation}\n"
            "a + \\text{A+B-C} + \\mbox{X+Y-Z}\n"
            "\\end{equation}\n",
        )

    def test_collapsed_equation_newlines_insert_separator_spaces(self) -> None:
        """Collapsed math newlines keep token boundaries readable."""

        source = (
            "\\begin{equation}\n"
            "\\label{eq:holder-synthesis-nonhomogeneous-top-scale}\n"
            "\\|G\\|_{\\mathcal{C}^{\\alpha}_{t_0}(\\R^d)}\n"
            "\\lesssim \n"
            "A_{t_0}. \n"
            "\\end{equation}\n"
        )

        transformed = transform_text(source)

        self.assertEqual(
            transformed,
            "\\begin{equation}\n"
            "\\label{eq:holder-synthesis-nonhomogeneous-top-scale}\n"
            "\\|G\\|_{\\mathcal{C}^{\\alpha}_{t_0}(\\R^d)} \\lesssim A_{t_0}.\n"
            "\\end{equation}\n",
        )

    def test_inline_opening_label_forces_separate_label_and_relation_split(self) -> None:
        """Inline opening labels move to their own line and long equations split at relations."""

        source = (
            "\\begin{equation}\\label{eq:homogeneous-calderon-formula}\n"
            "\\lim_{\\varepsilon\\to0^ + } \\dot{\\mc{R}}_{\\tilde{\\psi}} \n"
            "\\left[\\1_{\\varepsilon<t<\\varepsilon^{ - 1}}\\Em_\\psi[f]\\right] = f "
            "\\qquad \\text{in } \\Sch'(\\R^d).\n"
            "\\end{equation}\n"
        )

        transformed = transform_text(source)

        self.assertEqual(
            transformed,
            "\\begin{equation}\n"
            "\\label{eq:homogeneous-calderon-formula}\n"
            "\\lim_{\\varepsilon\\to0^ + } \\dot{\\mc{R}}_{\\tilde{\\psi}} "
            "\\left[\\1_{\\varepsilon<t<\\varepsilon^{ - 1}}\\Em_\\psi[f]\\right] \n"
            "= f \\qquad \\text{in } \\Sch'(\\R^d).\n"
            "\\end{equation}\n",
        )

    def test_bracket_display_math_is_reformatted(self) -> None:
        """Bracketed display math is treated as a top-level math container."""

        source = (
            "\\[\n"
            "  a=b+c\n"
            "  +d\n"
            "\\]\n"
        )

        transformed = transform_text(source)

        self.assertEqual(
            transformed,
            "\\[\n"
            "a=b + c + d\n"
            "\\]\n",
        )

    def test_aligned_subenvironment_inside_display_math_is_reformatted(self) -> None:
        """Nested aligned environments are reformatted unless blacklisted."""

        source = (
            "\\[\n"
            "\\begin{aligned}\n"
            "  a&=b+c\\\\\n"
            "   &\\lesssim d\n"
            "\\end{aligned}\n"
            "\\]\n"
        )

        transformed = transform_text(source)

        self.assertEqual(
            transformed,
            "\\[\n"
            "\\begin{aligned}\n"
            "a & =b + c\n"
            "\\\\\n"
            "& \\lesssim d\n"
            "\\end{aligned}\n"
            "\\]\n",
        )

    def test_large_aligned_display_keeps_alignment_marker_with_relation(self) -> None:
        """Long aligned rows do not split between ``&`` and the relation symbol."""

        source = (
            "\\[\n"
            "\\begin{aligned}\n"
            "  \\|T_m f\\|_{\\mathcal{C}^{\\beta}_{t_0}(\\R^d)}\n"
            "   & \\lesssim\n"
            "  \\|\\Em_\\varphi[T_m f](\\cdot,t_0)\\|_{L^\\infty(\\R^d)}\n"
            "  +\n"
            "  t_0^\\beta\n"
            "  \\left\\|\n"
            "  \\1_{0<r<t_0}\n"
            "  r^{-\\beta}\n"
            "  \\Em_\\psi[T_m f](\\cdot,r)\n"
            "  \\right\\|_{L^\\infty(\\R^d\\times(0,t_0))} \\\\\n"
            "   & \\lesssim\n"
            "  \\|m\\|_{\\mf{M}^{(t_0)}_{s,M_0}}\n"
            "  (A_0+A_1)                              \\\\\n"
            "   & \\lesssim\n"
            "  \\|m\\|_{\\mf{M}^{(t_0)}_{s,M_0}}\n"
            "  \\|f\\|_{\\mathcal{C}^{\\alpha}_{t_0}(\\R^d)}.\n"
            "\\end{aligned}\n"
            "\\]\n"
        )

        transformed = transform_text(source)

        self.assertIn("& \\lesssim", transformed)
        self.assertNotIn("& \n\\lesssim", transformed)
        self.assertNotIn("&\n\\lesssim", transformed)

    def test_aligned_optional_argument_stays_on_begin_line(self) -> None:
        """An aligned optional argument stays attached to ``\\begin{aligned}``."""

        source = (
            "\\[\n"
            "\\begin{aligned}[t]\n"
            "  a&=b+c\\\\\n"
            "  &\\lesssim d\n"
            "\\end{aligned}\n"
            "\\]\n"
        )

        transformed = transform_text(source)

        self.assertIn("\\begin{aligned}[t]\n", transformed)
        self.assertNotIn("\\begin{aligned}\n[t]", transformed)
        self.assertNotIn("\\begin{aligned}\n[t]\n", transformed)

    def test_relation_priority_beats_addition_priority(self) -> None:
        """Long lines split at relation symbols before falling back to ``+``."""

        source = (
            "\\begin{equation}\n"
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
            " = bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb + c\n"
            "\\end{equation}\n"
        )

        transformed = transform_text(source, max_width=95)

        self.assertIn("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa \n= ", transformed)
        self.assertNotIn("bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb + \n", transformed)

    def test_space_fallback_prefers_shallow_depth_over_superscript_contents(self) -> None:
        """Fallback space splitting avoids breaking inside grouped exponent contents when possible."""

        source = (
            "\\begin{equation}\n"
            "\\left\\| \\1_{0<r<t_0} r^{-\\beta} \\Em_\\psi[T_m f](\\cdot,r) \\right\\|_{L^\\infty(\\R^d\\times(0,t_0))}\n"
            "\\end{equation}\n"
        )

        transformed = transform_text(source, max_width=55)

        self.assertNotIn("r^{ \n- \\beta}", transformed)
        self.assertNotIn("r^{\n- \\beta}", transformed)

    def test_relation_macro_prefixes_do_not_match_inside_left(self) -> None:
        """Relation macros like ``\\le`` do not falsely match inside ``\\left``."""

        source = (
            "\\[\n"
            "\\begin{aligned}\n"
            "  \\|T_m f\\|_{\\mathcal{C}^{\\beta}_{t_0}(\\R^d)}\n"
            "   & \\lesssim\n"
            "  \\|\\Em_\\varphi[T_m f](\\cdot,t_0)\\|_{L^\\infty(\\R^d)}\n"
            "  +\n"
            "  t_0^\\beta\n"
            "  \\left\\|\n"
            "  \\1_{0<r<t_0}\n"
            "  r^{-\\beta}\n"
            "  \\Em_\\psi[T_m f](\\cdot,r)\n"
            "  \\right\\|_{L^\\infty(\\R^d\\times(0,t_0))}\n"
            "\\end{aligned}\n"
            "\\]\n"
        )

        transformed = transform_text(source, max_width=95)

        self.assertIn("\\|_{L^\\infty(\\R^d)} \n+ t_0^\\beta", transformed)
        self.assertNotIn("t_0^\\beta \n\\left\\|", transformed)

    def test_inline_environment_does_not_gain_boundary_newlines(self) -> None:
        """Inline environment bodies are not forced onto separate lines."""

        source = "A \\begin{equation}a+b\\end{equation} B"

        transformed = transform_text(source)

        self.assertEqual(transformed, "A \\begin{equation}a + b\\end{equation} B")
