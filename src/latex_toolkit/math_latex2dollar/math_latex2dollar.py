r"""This module converts command-style LaTeX math delimiters to dollar delimiters."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from latex_toolkit.math_dollar2latex.math_dollar2latex import (
    _run_command,
    _process_file,
    transform_text as _transform_text,
)


def transform_text(source: str) -> str:
    r"""Convert ``\(...\)`` to ``$...$`` and ``\[...\]`` to ``$$...$$``.

    Complete documents are transformed only inside top-level ``document``
    environments. Inputs without a document environment are treated as LaTeX
    fragments, and math contents are preserved exactly.

    Parameters
    ----------
    source : str
        LaTeX source in complete-document or fragment form.

    Returns
    -------
    str
        Source with command-style math delimiters replaced.

    Examples
    --------
    Basic usage:

    >>> transform_text(r"Inline \(x\) and display \[y\].")
    'Inline $x$ and display $$y$$.'
    """
    return _transform_text(source, reverse=True)


def _process_file(input_path: Path, output_path: Path) -> Path:
    """Transform one UTF-8 LaTeX file and write a separate UTF-8 result.

    Parameters
    ----------
    input_path : pathlib.Path
        Source file to read without modifying.
    output_path : pathlib.Path
        Destination to create or replace with transformed source.

    Returns
    -------
    pathlib.Path
        The destination supplied by the caller.

    Raises
    ------
    OSError
        The source cannot be read or the destination cannot be written.
    """
    return _process_file(input_path, output_path, reverse=True)


def main(argv: Sequence[str] | None = None) -> int:
    """Run conversion in file, clipboard, or standard-stream mode.

    Parameters
    ----------
    argv : sequence of str, optional
        Command-line arguments without the executable name.

    Returns
    -------
    int
        Process exit status; zero indicates success.

    Raises
    ------
    SystemExit
        Arguments select incompatible input or output modes.
    """
    return _run_command(argv, reverse=True)


if __name__ == "__main__":
    raise SystemExit(main())
