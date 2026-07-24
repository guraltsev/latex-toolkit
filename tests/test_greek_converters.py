r"""Protect Greek notation conversion within parsed LaTeX math.

The tests exercise both public text APIs and real LaTeX parsing. File,
clipboard, and standard-stream command boundaries are covered elsewhere.
"""

from latex_toolkit.greek_latex2unicode import transform_text as macros_to_unicode
from latex_toolkit.greek_unicode2latex import transform_text as unicode_to_macros


def test_unicode_greek_symbols_become_macros_only_in_math() -> None:
    """Greek symbols in inline and display math become their LaTeX macros."""
    source = "Greek α stays prose; $α + ϕ + Ω$ and \\begin{align}β &= Γ\\end{align}."

    assert unicode_to_macros(source) == (
        "Greek α stays prose; $\\alpha + \\varphi + \\Omega$ and "
        "\\begin{align}\\beta &= \\Gamma\\end{align}."
    )


def test_greek_macros_become_unicode_without_changing_prose_or_comments() -> None:
    """Recognized math macros convert while prose, comments, and longer names remain."""
    source = r"\alpha prose; $\alpha + \vartheta$ % \beta" + "\n" + r"\[\Omega + \alphabeta\]"

    assert macros_to_unicode(source) == r"\alpha prose; $α + ϑ$ % \beta" + "\n" + r"\[Ω + \alphabeta\]"


def test_epsilon_variants_round_trip_with_distinct_latex_macros() -> None:
    """Each Unicode epsilon variant retains its distinct spelling through conversion."""
    assert unicode_to_macros("$ε + ϵ$") == r"$\epsilon + \varepsilon$"
    assert macros_to_unicode(r"$\epsilon + \varepsilon$") == "$ε + ϵ$"


def test_complete_documents_preserve_the_preamble() -> None:
    """Only a complete document's body receives Greek notation conversion."""
    source = r"\newcommand{\foo}{$α$}" + "\n" + r"\begin{document}$α$\end{document}"

    assert unicode_to_macros(source) == (
        r"\newcommand{\foo}{$α$}" + "\n" + r"\begin{document}$\alpha$\end{document}"
    )
