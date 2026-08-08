"""Regularize whitespace in supported MyST Markdown prose."""
from collections.abc import Sequence
from latex_toolkit.lib.markdown import regularize_text, run_command

def transform_text(source: str) -> str:
    """Regularize supported Markdown prose whitespace.

    Parameters
    ----------
    source : str
        MyST Markdown source.

    Returns
    -------
    str
        Canonical prose wrapping with sensitive Markdown source unchanged.
    """
    return regularize_text(source)

def main(argv: Sequence[str] | None = None) -> int:
    """Run Markdown syntax regularization in a selected input mode."""
    return run_command(argv, transform=transform_text, description="Regularize supported MyST Markdown whitespace.")
