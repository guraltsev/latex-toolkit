#!/usr/bin/env python3
r"""CLI for converting TeXmacs ``\tmscript`` arrays to ``\substack``."""

from __future__ import annotations

from pathlib import Path
import argparse

from latex_toolkit.lib.backup import DEFAULT_BACKUP_DIR, backup_file
from latex_toolkit.lib.core import write_tex_file
from latex_toolkit.lib.logging_config import run_clipboard_transform, run_command
from .transform import convert_tex_file, convert_text

# This command overwrites source files unless output or clipboard mode is used.
OVERWRITES_SOURCE_TEX = True


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser.

    Returns
    -------
    argparse.ArgumentParser
        Parser configured for TeXmacs script-array conversion.
    """

    parser = argparse.ArgumentParser(
        prog="tmscript2substack",
        description=(
            "Rewrite \\tmscript{\\begin{array}{c} ... \\end{array}} as \\substack{...}. "
            "By default the input file is overwritten; use -o/--output to write elsewhere."
        ),
    )
    parser.add_argument("input", nargs="?", help="Input .tex file.")
    parser.add_argument(
        "--clipboard",
        action="store_true",
        help="Read LaTeX from the clipboard and replace it with converted output.",
    )
    parser.add_argument(
        "-o",
        "--output",
        "--output-file",
        dest="output",
        help="Write converted output to this path instead of overwriting the input file.",
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


def transform_text(text: str) -> str:
    """Rewrite TeXmacs centered script arrays in ``text`` as ``\\substack``.

    Parameters
    ----------
    text : str
        LaTeX source text to transform.

    Returns
    -------
    str
        Source text with converted ``\\tmscript`` constructs.
    """

    return convert_text(text)


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

        if args.clipboard:
            if args.input is not None or args.output is not None:
                parser.error("--clipboard cannot be combined with input or output paths.")
            run_clipboard_transform("tmscript2substack", transform_text)
            return 0

        if args.input is None:
            parser.error("the following arguments are required: input")

        input_path = Path(args.input).expanduser().resolve()
        converted = convert_tex_file(input_path)
        output_path = Path(args.output).expanduser().resolve() if args.output else input_path

        if output_path == input_path and not args.no_backup:
            backup_file(input_path, args.backup_dir)

        write_tex_file(converted, output_path)
        return 0

    return run_command("tmscript2substack", run)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
