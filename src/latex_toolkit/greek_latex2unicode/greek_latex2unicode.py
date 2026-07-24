r"""This module converts LaTeX Greek macros in math to Unicode Greek letters.

The ``transform_text(...)`` API supports in-memory conversion and ``main(...)``
supports file, clipboard, and standard-stream workflows. Only recognized macros in
parsed math regions are changed; prose, comments, and document preambles are
preserved.
"""

from __future__ import annotations

from collections.abc import Sequence

from latex_toolkit.greek_unicode2latex.greek_unicode2latex import _run_command
from latex_toolkit.greek_unicode2latex.greek_unicode2latex import transform_text as _transform_text


def transform_text(source: str) -> str:
    r"""Convert recognized LaTeX Greek macros to Unicode in math mode.

    Parameters
    ----------
    source : str
        LaTeX source in complete-document or fragment form.

    Returns
    -------
    str
        Source with recognized Greek macros replaced in math mode only.
    """
    return _transform_text(source, reverse=True)


def main(argv: Sequence[str] | None = None) -> int:
    """Run LaTeX Greek to Unicode conversion in a selected input mode.

    Parameters
    ----------
    argv : sequence of str, optional
        Command-line arguments without the executable name.

    Returns
    -------
    int
        Zero after a completed transformation.

    Raises
    ------
    SystemExit
        Arguments select incompatible input or output modes.
    """
    return _run_command(argv, reverse=True)
