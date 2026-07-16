r"""Protect the combined syntax-then-sentence transformation behavior.

The tests run both real public transformations, including pylatexenc and the
pinned Snapper formatter. CLI boundary behavior and internal call structure
are outside this module's scope.
"""

from src.syntax_then_sentence_transformer import transform_text


def test_pipeline_regularizes_syntax_before_formatting_sentences() -> None:
    """One call applies syntax cleanup before sentence boundary formatting."""
    source = "  First sentence with $1+\n  1=2$. Second sentence."

    assert transform_text(source) == (
        "First sentence with $1+1=2$.\nSecond sentence."
    )


def test_pipeline_combines_heading_and_sentence_layout() -> None:
    """Regularized heading spacing remains while following prose is formatted."""
    source = "  \\section{Title}\nFirst sentence. Second sentence."

    assert transform_text(source) == (
        "\\section{Title}\n\nFirst sentence.\nSecond sentence."
    )


def test_pipeline_is_idempotent() -> None:
    """A second combined pass produces byte-identical source."""
    once = transform_text("  First sentence. Second sentence.")

    assert transform_text(once) == once
