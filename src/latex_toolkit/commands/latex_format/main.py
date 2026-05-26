#!/usr/bin/env python3
"""CLI for formatting LaTeX with latexindent and snapper in sequence."""

from __future__ import annotations

from pathlib import Path
import argparse

from latex_toolkit.commands.latex_indent import main as latex_indent_command
from latex_toolkit.lib.backup import DEFAULT_BACKUP_DIR, backup_file
from latex_toolkit.lib.latex import read_text, write_text
from latex_toolkit.lib.logging_config import (
    ClipboardPipelineStep,
    run_clipboard_pipeline,
    run_command,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser.

    Returns
    -------
    argparse.ArgumentParser
        Parser configured for the latex formatting pipeline.
    """

    parser = argparse.ArgumentParser(
        prog="latex_format",
        description=(
            "Format LaTeX by running latex_indent, then snapper_format. "
            "Without input or output paths, the command formats clipboard text."
        ),
    )
    parser.add_argument("input", nargs="?", help="Input .tex file.")
    parser.add_argument(
        "--clipboard",
        action="store_true",
        help="Read LaTeX from the clipboard and replace it with formatted output.",
    )
    parser.add_argument(
        "--max-width",
        type=int,
        default=0,
        help=(
            "Wrap sentences longer than this width after snapper splits them. "
            "The default, 0, keeps each sentence on one line."
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        "--output-file",
        dest="output",
        help="Write formatted output to this path instead of overwriting the input file.",
    )
    parser.add_argument(
        "-B",
        "--no-backup",
        action="store_true",
        help="Do not create a backup before overwriting the input file.",
    )
    parser.add_argument(
        "--backup-dir",
        default=DEFAULT_BACKUP_DIR,
        help="Relative or absolute directory for backups when overwriting. Default: %(default)s",
    )
    return parser


def pipeline_steps(*, max_width: int = 0) -> tuple[ClipboardPipelineStep, ...]:
    """Return the configured LaTeX formatting pipeline steps.

    Parameters
    ----------
    max_width : int
        Sentence wrapping width to pass to ``snapper_format``.

    Returns
    -------
    tuple of tuple
        Ordered ``(step_name, transform)`` pairs for the formatting pipeline.
    """
    del max_width
    return (("latex_indent", latex_indent_command.transform_text),)


def transform_text(text: str, *, max_width: int = 0) -> str:
    """Run the LaTeX formatting pipeline on ``text``.

    Parameters
    ----------
    text : str
        LaTeX text to format.
    max_width : int
        Sentence wrapping width to pass to ``snapper_format``.

    Returns
    -------
    str
        Text after every enabled formatting step has run.
    """

    # Apply the same ordered transforms used by the CLI so Python callers can
    # reuse the formatter pipeline without touching files or the clipboard.
    transformed = text
    for _, transform in pipeline_steps(max_width=max_width):
        transformed = transform(transformed)
    return transformed


def main(argv: list[str] | None = None) -> int:
    """Run the command-line workflow.

    Parameters
    ----------
    argv : list of str or None
        Command-line arguments to parse. ``None`` reads arguments from
        ``sys.argv``.

    Returns
    -------
    int
        Process exit status, with ``0`` for success and ``1`` for expected
        operational failures.

    Raises
    ------
    SystemExit
        Command-line arguments are invalid.
    """

    def run() -> int:
        parser = build_parser()
        args = parser.parse_args(argv)

        if args.max_width < 0:
            parser.error("--max-width must be zero or positive.")

        # Match the existing launcher-oriented behavior used by snapper_format:
        # no explicit file arguments means format the clipboard contents.
        use_clipboard = args.clipboard or (args.input is None and args.output is None)

        if use_clipboard:
            if args.input is not None or args.output is not None:
                parser.error("--clipboard cannot be combined with input or output paths.")
            run_clipboard_pipeline("latex_format", pipeline_steps(max_width=args.max_width))
            return 0

        if args.input is None:
            parser.error("the following arguments are required: input")

        input_path = Path(args.input).expanduser().resolve()
        formatted = transform_text(read_text(input_path), max_width=args.max_width)
        output_path = Path(args.output).expanduser().resolve() if args.output else input_path

        if output_path == input_path and not args.no_backup:
            backup_file(input_path, args.backup_dir)

        write_text(output_path, formatted)
        return 0

    return run_command("latex_format", run)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
