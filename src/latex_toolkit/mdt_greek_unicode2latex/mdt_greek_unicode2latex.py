"""Convert Unicode Greek symbols only inside MyST Markdown TeX math."""
from collections.abc import Sequence
from latex_toolkit.lib.markdown import greek_unicode_to_latex_text, run_command

def transform_text(source: str) -> str:
    """Convert Unicode Greek symbols only inside Markdown math spans.

    Parameters
    ----------
    source : str
        MyST Markdown source.

    Returns
    -------
    str
        Source with recognized math symbols converted to LaTeX macros.
    """
    return greek_unicode_to_latex_text(source)

def main(argv: Sequence[str] | None = None) -> int:
    """Run Markdown Unicode Greek conversion in a selected input mode."""
    return run_command(argv, transform=transform_text, description="Convert Unicode Greek symbols inside Markdown math.")
