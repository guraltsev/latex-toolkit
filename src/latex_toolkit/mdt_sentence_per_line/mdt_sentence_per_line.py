"""Put supported MyST Markdown prose sentences on physical source lines."""
from collections.abc import Sequence
from latex_toolkit.lib.markdown import run_command, sentence_text

def transform_text(source: str) -> str:
    """Put supported Markdown prose sentences on physical source lines.

    Parameters
    ----------
    source : str
        MyST Markdown source.

    Returns
    -------
    str
        Sentence-per-line Markdown source with protected constructs unchanged.
    """
    return sentence_text(source)

def main(argv: Sequence[str] | None = None) -> int:
    """Run Markdown sentence formatting in a selected input mode."""
    return run_command(argv, transform=transform_text, description="Put supported MyST Markdown sentences on source lines.")
