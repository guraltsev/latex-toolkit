r"""Expose the regularize-then-sentence LaTeX transformation pipeline."""

from .syntax_then_sentence_transformer import process_file, transform_text

__all__ = ["process_file", "transform_text"]
