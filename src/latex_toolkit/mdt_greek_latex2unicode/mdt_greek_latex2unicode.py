"""Convert recognized LaTeX Greek macros only inside MyST Markdown math."""
from collections.abc import Sequence
from latex_toolkit.lib.markdown import greek_latex_to_unicode_text, run_command

def transform_text(source: str) -> str:
    """Convert recognized LaTeX Greek macros only inside Markdown math spans.

    Parameters
    ----------
    source : str
        MyST Markdown source.

    Returns
    -------
    str
        Source with recognized math macros converted to Unicode symbols.
    """
    return greek_latex_to_unicode_text(source)

def main(argv: Sequence[str] | None = None) -> int:
    """Run Markdown LaTeX Greek conversion in a selected input mode."""
    return run_command(argv, transform=transform_text, description="Convert LaTeX Greek macros inside Markdown math.")
