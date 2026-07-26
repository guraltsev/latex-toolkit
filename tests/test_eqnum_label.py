r"""Protect user-visible equation-number label normalization behavior.

The tests exercise the public text transformation and its real LaTeX parsing
boundary. File and clipboard workflows are outside this module's scope.
"""

from latex_toolkit.eqnum_label import transform_text


def test_standalone_trailing_pair_moves_to_the_start_of_bracket_display() -> None:
    """One trailing pair becomes the first display-content line with one space."""
    source = "\\[\n  x=1\n  \\eqnum\\label{eq:x}\n\\]"

    assert transform_text(source) == "\\[\n\\eqnum \\label{eq:x}\n  x=1\n\\]"


def test_equation_environment_pair_moves_to_the_start() -> None:
    """A standalone pair moves after an equation opener without changing formula layout."""
    source = "\\begin{equation}\n  x=1\n  \\eqnum  \\label{eq:x}\n\\end{equation}"

    assert transform_text(source) == (
        "\\begin{equation}\n\\eqnum \\label{eq:x}\n  x=1\n\\end{equation}"
    )


def test_multirow_display_keeps_pair_position_but_normalizes_its_spacing() -> None:
    """An align label remains with its row while adjacent macro spacing is canonicalized."""
    source = "\\begin{align}\n  a&=b \\eqnum\\label{eq:a}\\\\\n  c&=d\n\\end{align}"

    assert transform_text(source) == (
        "\\begin{align}\n  a&=b \\eqnum \\label{eq:a}\\\\\n  c&=d\n\\end{align}"
    )


def test_comment_text_does_not_produce_an_equation_label() -> None:
    """A commented pair remains unchanged while a real pair is normalized."""
    source = "\\[\n  x=1 % \\eqnum\\label{eq:comment}\n  \\eqnum\\label{eq:x}\n\\]"

    assert transform_text(source) == (
        "\\[\n\\eqnum \\label{eq:x}\n  x=1 % \\eqnum\\label{eq:comment}\n\\]"
    )
