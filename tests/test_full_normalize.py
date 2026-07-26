r"""Protect the complete LaTeX normalization behavior.

The tests run the real complete pipeline, including pylatexenc and the
pinned Snapper formatter. CLI boundary behavior and internal call structure
are outside this module's scope.
"""

from latex_toolkit.full_normalize import transform_text


def test_full_normalize_regularizes_syntax_around_sentence_formatting() -> None:
    """One call produces fully normalized sentence-per-line LaTeX."""
    source = "  First sentence with $1+\n  1=2$. Second sentence."

    assert transform_text(source) == (
        "First sentence with \\(1+1=2\\).\nSecond sentence."
    )


def test_full_normalize_combines_heading_and_sentence_layout() -> None:
    """Normalized heading spacing accompanies formatted following prose."""
    source = "  \\section{Title}\nFirst sentence. Second sentence."

    assert transform_text(source) == (
        "\\section{Title}\n\nFirst sentence.\nSecond sentence."
    )


def test_full_normalize_braces_parsed_arguments_and_math_scripts() -> None:
    """Macro arguments and math scripts are explicit in normalized output."""
    source = "  First with $\\mathcal A + x_1$. Second sentence."

    assert transform_text(source) == (
        "First with \\(\\mathcal{A} + x_{1}\\).\nSecond sentence."
    )


def test_full_normalize_places_a_trailing_equation_label_first() -> None:
    """The composed workflow moves an eligible equation-number label after its opener."""
    source = "\\[\n  x=1\n  \\eqnum\\label{eq:x}\n\\]"

    assert transform_text(source) == "\\[\n\\eqnum \\label{eq:x}\n  x=1\n\\]"


def test_full_normalize_is_idempotent() -> None:
    """A second full-normalization pass produces byte-identical source."""
    once = transform_text("  First sentence. Second sentence.")

    assert transform_text(once) == once
