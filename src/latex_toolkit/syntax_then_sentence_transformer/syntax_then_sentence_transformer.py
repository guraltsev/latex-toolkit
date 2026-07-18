r"""Regularize LaTeX syntax before formatting prose one sentence per line.

Call ``transform_text(...)`` to run the two transformations in their required
order. The command-line interface provides the template's separate-output file
workflow and clipboard mode.
"""

from __future__ import annotations

import argparse
import importlib
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path
from types import ModuleType

from ..sentence_per_line_transformer import (
    transform_text as transform_sentences,
)
from ..syntax_regularizer import transform_text as regularize_syntax


class _DependencyManager:
    """Load configured modules and install their distributions when unavailable."""

    def __init__(self, distributions: dict[str, str]) -> None:
        self.distributions = dict(distributions)

    def require(self, import_name: str) -> ModuleType:
        """Import a configured module, installing it when unavailable."""
        requirement = self.distributions[import_name]
        try:
            return importlib.import_module(import_name)
        except ModuleNotFoundError as error:
            missing_requested_path = error.name == import_name or import_name.startswith(
                f"{error.name}."
            )
            if not missing_requested_path:
                raise

        subprocess.check_call([sys.executable, "-m", "pip", "install", requirement])
        importlib.invalidate_caches()
        package_name = import_name.partition(".")[0]
        for module_name in tuple(sys.modules):
            if module_name == package_name or module_name.startswith(
                f"{package_name}."
            ):
                sys.modules.pop(module_name, None)
        return importlib.import_module(import_name)


RUNTIME_DEPENDENCIES = _DependencyManager({"pyperclip": "pyperclip>=1.9"})


def transform_text(source: str) -> str:
    r"""Regularize LaTeX syntax and then format prose sentence by sentence.

    Parameters
    ----------
    source : str
        LaTeX source in complete-document or fragment form.

    Returns
    -------
    str
        Source after syntax regularization followed by sentence-per-line
        formatting.

    Raises
    ------
    RuntimeError
        The sentence formatter is unavailable or exits unsuccessfully.

    Examples
    --------
    Basic usage:

    >>> transform_text("  First with $1+\\n1=2$. Second.")
    'First with $1+1=2$.\nSecond.'
    """
    regularized = regularize_syntax(source)
    return transform_sentences(regularized)


def process_file(input_path: Path, output_path: Path) -> Path:
    """Run the pipeline for one UTF-8 file and write a separate result.

    Parameters
    ----------
    input_path : pathlib.Path
        Source file to read without modifying.
    output_path : pathlib.Path
        Destination to create or replace after both transformations succeed.

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
    # Finish both stages before opening the destination, preserving any
    # existing output when either transformation fails.
    source = input_path.read_text(encoding="utf-8")
    transformed = transform_text(source)
    output_path.write_text(transformed, encoding="utf-8")
    return output_path


def main(argv: Sequence[str] | None = None) -> int:
    """Run the combined transformer in file or clipboard mode.

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
    if args.input_file is None and not args.clipboard:
        args.clipboard = True
    if bool(args.input_file) == args.clipboard:
        parser.error("provide an input file or --clipboard, but not both")
    if args.clipboard and args.output_file is not None:
        parser.error("--output cannot be used with --clipboard")

    if args.clipboard:
        _transform_clipboard()
        return 0

    output_path = args.output_file or _default_output_path(args.input_file)
    process_file(args.input_file, output_path)
    print(f"Transformed file written to: {output_path}")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    """Build the command-line interface for the combined workflow."""
    parser = argparse.ArgumentParser(
        description=(
            "Regularize LaTeX syntax, then put each prose sentence on its own line."
        )
    )
    parser.add_argument("input_file", nargs="?", type=Path, help="UTF-8 LaTeX file")
    parser.add_argument(
        "-o",
        "--output",
        "--output-file",
        dest="output_file",
        type=Path,
        help="destination path (default: INPUT_regularized_sentences.tex)",
    )
    parser.add_argument(
        "--clipboard",
        action="store_true",
        help="transform the system clipboard instead of a file",
    )
    return parser


def _default_output_path(input_path: Path) -> Path:
    """Return a sibling path marked as regularized and sentence-formatted."""
    suffix = input_path.suffix or ".tex"
    stem = input_path.stem if input_path.suffix else input_path.name
    return input_path.with_name(f"{stem}_regularized_sentences{suffix}")


def _transform_clipboard() -> None:
    """Transform nonempty clipboard text and copy it back only on success."""
    pyperclip = RUNTIME_DEPENDENCIES.require("pyperclip")

    source = pyperclip.paste()
    if not source.strip():
        print("Clipboard is empty; nothing was changed.")
        return
    pyperclip.copy(transform_text(source))
    print("Regularized sentence-per-line LaTeX written back to the clipboard.")


if __name__ == "__main__":
    raise SystemExit(main())
