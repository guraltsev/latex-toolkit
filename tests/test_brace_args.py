r"""Protect public LaTeX argument and math-script bracing behavior.

The tests exercise the real pylatexenc parser through the public text API.
CLI file and clipboard boundaries, parser internals, and custom macros beyond
the bundled mathematical shorthand are outside this module's scope.
"""

from latex_toolkit.brace_args import transform_text


def test_macro_arguments_and_math_scripts_receive_braces() -> None:
    """Recognized macro arguments and ungrouped scripts become explicit groups."""
    source = (
        r"$\mathcal A + \FT f + \mb b + \mbb B + \mbf v + \mc L "
        r"+ \mf f + \ms S + \mathbf x + \frac12 + \sqrt[3]x + a_1^2$"
    )

    assert transform_text(source) == (
        r"$\mathcal{A} + \FT{f} + \mb{b} + \mbb{B} + \mbf{v} + \mc{L} "
        r"+ \mf{f} + \ms{S} + \mathbf{x} + \frac{1}{2} + \sqrt[3]{x} "
        r"+ a_{1}^{2}$"
    )


def test_scripted_macro_contains_its_complete_argument_expression() -> None:
    """A macro and its parsed arguments form one explicitly braced script."""
    assert transform_text(r"$x^\frac12$") == r"$x^{\frac{1}{2}}$"


def test_complete_document_preserves_preamble() -> None:
    """Only a complete document's body receives argument and script braces."""
    source = (
        r"\newcommand{\mc}[1]{\mathcal #1}" "\n"
        r"\begin{document}$\mc A + y_2$\end{document}"
    )

    assert transform_text(source) == (
        r"\newcommand{\mc}[1]{\mathcal #1}" "\n"
        r"\begin{document}$\mc{A} + y_{2}$\end{document}"
    )
