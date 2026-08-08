"""Convert recognized dollar math to command-style TeX delimiters in MyST."""
from collections.abc import Sequence
from latex_toolkit.lib.markdown import dollar_to_latex_text, run_command

def transform_text(source: str) -> str:
    """Convert explicit safe dollar math delimiters to TeX commands.

    Parameters
    ----------
    source : str
        MyST Markdown source.

    Returns
    -------
    str
        Source with recognized math delimiters converted and bare dollars preserved.
    """
    return dollar_to_latex_text(source)

def main(argv: Sequence[str] | None = None) -> int:
    """Run reverse Markdown math delimiter conversion in a selected input mode."""
    return run_command(argv, transform=transform_text, description="Convert recognized Markdown dollar math to TeX delimiters.")
