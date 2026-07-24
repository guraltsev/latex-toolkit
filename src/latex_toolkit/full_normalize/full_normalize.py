r"""This module fully normalizes LaTeX syntax and prose sentence layout.

The ``transform_text(...)`` API converts dollar-delimited math, regularizes
syntax, braces parsed macro arguments and math scripts, formats prose one
sentence per line, then regularizes syntax again. The command-line interface
provides file, clipboard, and standard-stream workflows.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from ..sentence_per_line import (
    transform_text as transform_sentences,
)
from ..brace_args import transform_text as brace_arguments
from ..math_dollar2latex import transform_text as convert_math_delimiters
from ..syntax_regularizer import transform_text as regularize_syntax
from latex_toolkit.lib.dependencies import DependencyManager
from latex_toolkit.lib.backup import backup_file


def transform_text(source: str) -> str:
    r"""Fully normalize LaTeX syntax and prose sentence layout.

    Parameters
    ----------
    source : str
        LaTeX source in complete-document or fragment form.

    Returns
    -------
    str
        Source after dollar-to-command math conversion, syntax regularization,
        macro-argument and math-script bracing, sentence-per-line formatting,
        and final syntax regularization.

    Raises
    ------
    RuntimeError
        The sentence formatter is unavailable or exits unsuccessfully.

    Examples
    --------
    Basic usage:

    >>> transform_text("  First with $1+\\n1=2$. Second.")
    'First with \\(1+1=2\\).\nSecond.'
    """
    # Standardize math delimiters before layout processing so display formulas
    # and inline formulas both follow the command-style source convention.
    command_delimited = convert_math_delimiters(source)

    # Establish a regular source layout and explicit parsed argument boundaries
    # before the prose formatter reads the document structure.
    regularized = regularize_syntax(command_delimited)
    braced = brace_arguments(regularized)
    sentences = transform_sentences(braced)

    # Reapply source-layout rules after the sentence formatter has rewritten
    # prose line boundaries.
    return regularize_syntax(sentences)


def _process_file(input_path: Path, output_path: Path) -> Path:
    """Run the pipeline for one UTF-8 file and write a separate result.

    Parameters
    ----------
    input_path : pathlib.Path
        Source file to read without modifying.
    output_path : pathlib.Path
        Destination to create or replace after all transformations succeed.

    Returns
    -------
    pathlib.Path
        The destination supplied by the caller.

    Raises
    ------
    OSError
        The source cannot be read or the destination cannot be written.
    RuntimeError
        Sentence-per-line formatting fails before the destination is opened.
    """
    # Finish every stage before opening the destination, preserving any
    # existing output when either transformation fails.
    source = input_path.read_text(encoding="utf-8")
    transformed = transform_text(source)
    output_path.write_text(transformed, encoding="utf-8")
    return output_path


def main(argv: Sequence[str] | None = None) -> int:
    """Run normalization in file, clipboard, or standard-stream mode.

    With no arguments, the command transforms the system clipboard.

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
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.input_file is None and not args.clipboard and not args.stdin:
        args.clipboard = True
    selected_inputs = sum((args.input_file is not None, args.clipboard, args.stdin))
    if selected_inputs != 1:
        parser.error("provide an input file, --clipboard, or --stdin")
    if (args.clipboard or args.stdin) and args.output_file is not None:
        parser.error("--output cannot be used with --clipboard or --stdin")

    if args.clipboard:
        _transform_clipboard()
        return 0
    if args.stdin:
        sys.stdout.write(transform_text(sys.stdin.read()))
        return 0

    if args.output_file is None and not args.no_backup:
        backup_file(args.input_file)
    output_path = args.output_file or args.input_file
    _process_file(args.input_file, output_path)
    print(f"Transformed file written to: {output_path}")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    """Build the command-line interface for complete normalization."""
    parser = argparse.ArgumentParser(
        description=(
            "Convert dollar-delimited math, regularize LaTeX syntax, brace "
            "parsed macro arguments and math scripts, put each prose sentence "
            "on its own line, then regularize syntax again."
        )
    )
    parser.add_argument("input_file", nargs="?", type=Path, help="UTF-8 LaTeX file")
    parser.add_argument(
        "-o",
        "--output",
        "--output-file",
        dest="output_file",
        type=Path,
        help="destination path; preserves INPUT and skips its backup",
    )
    parser.add_argument(
        "-B", "--no-backup", action="store_true", help="overwrite INPUT without a backup"
    )
    parser.add_argument(
        "--clipboard",
        action="store_true",
        help="transform the system clipboard instead of a file",
    )
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="read UTF-8 LaTeX from stdin and write the result to stdout",
    )
    return parser


# Keep only this command's dependency declarations at its external boundary.
RUNTIME_DEPENDENCIES = DependencyManager({"pyperclip": "pyperclip>=1.9"})


def _default_output_path(input_path: Path) -> Path:
    """Return a sibling path marked as fully normalized."""
    suffix = input_path.suffix or ".tex"
    stem = input_path.stem if input_path.suffix else input_path.name
    return input_path.with_name(f"{stem}_full_normalized{suffix}")


def _transform_clipboard() -> None:
    """Transform nonempty clipboard text and copy it back only on success."""
    pyperclip = RUNTIME_DEPENDENCIES.require("pyperclip")

    source = pyperclip.paste()
    if not source.strip():
        print("Clipboard is empty; nothing was changed.")
        return
    pyperclip.copy(transform_text(source))
    print("Fully normalized LaTeX written back to the clipboard.")


if __name__ == "__main__":
    raise SystemExit(main())
