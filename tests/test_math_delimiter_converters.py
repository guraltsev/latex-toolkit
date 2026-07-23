r"""Protect user-visible math delimiter conversion behavior.

The tests exercise the real pylatexenc parsing boundary through both public
text transformations. File and clipboard workflows are outside this module's
scope.
"""

import pytest

from latex_toolkit.math_dollar2latex import (
    transform_text as to_latex_delimiters,
)
from latex_toolkit.math_latex2dollar import (
    transform_text as to_dollar_math,
)


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("Inline $x + 1$.", r"Inline \(x + 1\)."),
        ("Display $$x + 1$$.", r"Display \[x + 1\]."),
        ("$x$ then $$y$$", r"\(x\) then \[y\]"),
    ],
    ids=["inline", "display", "mixed"],
)
def test_dollar_math_uses_command_style_delimiters(source: str, expected: str) -> None:
    """Dollar math delimiters change without altering their contents."""
    assert to_latex_delimiters(source) == expected


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (r"Inline \(x + 1\).", "Inline $x + 1$."),
        (r"Display \[x + 1\].", "Display $$x + 1$$."),
        (r"\(x\) then \[y\]", "$x$ then $$y$$"),
    ],
    ids=["inline", "display", "mixed"],
)
def test_command_style_math_uses_dollar_delimiters(source: str, expected: str) -> None:
    """Command-style math delimiters change without altering their contents."""
    assert to_dollar_math(source) == expected


def test_non_target_syntax_remains_byte_identical() -> None:
    """Escaped dollars, comments, and the other delimiter style stay unchanged."""
    source = "Price: \\$5. % $comment$\nAlready \\(x\\)."

    assert to_latex_delimiters(source) == source


def test_complete_documents_preserve_the_preamble() -> None:
    """Conversions in complete documents are limited to document bodies."""
    source = (
        "\\newcommand{\\sample}{$p$}\n\\begin{document}$b$ and $$c$$\\end{document}"
    )

    assert to_latex_delimiters(source) == (
        "\\newcommand{\\sample}{$p$}\n"
        "\\begin{document}\\(b\\) and \\[c\\]\\end{document}"
    )


def test_conversions_are_mutual_inverses_for_supported_math() -> None:
    """Applying both commands restores supported mixed math source exactly."""
    source = "Before $a\n + b$ and $$c = d$$ after."

    assert to_dollar_math(to_latex_delimiters(source)) == source
