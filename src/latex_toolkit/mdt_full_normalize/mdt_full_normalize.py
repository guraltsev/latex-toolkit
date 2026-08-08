"""Fully normalize supported MyST Markdown prose and TeX math.

Call ``transform_text(...)`` for in-memory source, or ``main(...)`` for the
standard file, clipboard, and standard-stream command contract.
"""
from collections.abc import Sequence
from latex_toolkit.lib.markdown import full_normalize_text, run_command

def transform_text(source: str) -> str:
    """Fully normalize supported MyST Markdown source.

    Parameters
    ----------
    source : str
        MyST Markdown source.

    Returns
    -------
    str
        Canonical source after supported whitespace, delimiter, bracing, and
        sentence-per-line transformations.
    """
    return full_normalize_text(source)

def main(argv: Sequence[str] | None = None) -> int:
    """Run complete Markdown normalization in a selected input mode."""
    return run_command(argv, transform=transform_text, description="Fully normalize supported MyST Markdown.")
