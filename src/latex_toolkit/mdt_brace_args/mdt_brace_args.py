"""Make TeX arguments and scripts explicit only inside Markdown math spans."""
from collections.abc import Sequence
from latex_toolkit.lib.markdown import brace_math_text, run_command

def transform_text(source: str) -> str:
    """Brace supported TeX arguments and scripts inside Markdown math.

    Parameters
    ----------
    source : str
        MyST Markdown source.

    Returns
    -------
    str
        Source with Markdown prose and protected regions unchanged.
    """
    return brace_math_text(source)

def main(argv: Sequence[str] | None = None) -> int:
    """Run Markdown math bracing in a selected input mode."""
    return run_command(argv, transform=transform_text, description="Brace TeX arguments and scripts inside Markdown math.")
