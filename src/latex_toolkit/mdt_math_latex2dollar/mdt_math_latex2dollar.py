"""Convert safe command-style TeX math delimiters in MyST Markdown."""
from collections.abc import Sequence
from latex_toolkit.lib.markdown import latex_to_dollar_text, run_command

def transform_text(source: str) -> str:
    """Convert command-style math delimiters in safe Markdown prose.

    Parameters
    ----------
    source : str
        MyST Markdown source.

    Returns
    -------
    str
        Source with supported ``\\(...\\)`` and line-oriented ``\\[...\\]`` delimiters converted.
    """
    return latex_to_dollar_text(source)

def main(argv: Sequence[str] | None = None) -> int:
    """Run Markdown math delimiter conversion in a selected input mode."""
    return run_command(argv, transform=transform_text, description="Convert safe Markdown TeX delimiters to dollar math.")
