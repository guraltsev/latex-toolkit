#!/usr/bin/env python3
"""CLI for converting between ``equation*`` and plain display math."""

from __future__ import annotations

from pathlib import Path
import argparse
import sys

from lib.backup import DEFAULT_BACKUP_DIR, backup_file
from lib.clipboard import read_clipboard_text, write_clipboard_text
from lib.core import write_tex_file
from lib.equation_star_displaymath import convert_tex_file, convert_text

# This command overwrites source files unless output or clipboard mode is used.
OVERWRITES_SOURCE_TEX = True


def build_parser(
    *,
    prog: str = "eqn-star2dmath",
    description: str | None = None,
    include_reverse: bool = True,
) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=prog,
        description=(
            description
            or (
                "Rewrite equation* environments as \\[ ... \\]. "
                "By default the input file is overwritten; use -o/--output to write elsewhere."
            )
        ),
    )
    parser.add_argument("input", nargs="?", help="Input .tex file.")
    parser.add_argument(
        "--clipboard",
        action="store_true",
        help="Read LaTeX from the clipboard and replace it with converted output.",
    )
    if include_reverse:
        parser.add_argument(
            "--reverse",
            action="store_true",
            help=(
                "Rewrite plain \\[ ... \\] blocks as equation* environments instead. "
                "Blocks whose body starts with standalone \\eqnum are left untouched."
            ),
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


def transform_text(text: str, *, reverse: bool = False) -> str:
    """Convert ``equation*`` and plain display math in ``text``.

    Parameters
    ----------
    text : str
        LaTeX source text to transform.
    reverse : bool
        ``False`` rewrites ``equation*`` as display math. ``True`` rewrites
        plain display math back to ``equation*``.

    Returns
    -------
    str
        Converted source text.
    """

    return convert_text(text, reverse=reverse)


def main(
    argv: list[str] | None = None,
    *,
    prog: str = "eqn-star2dmath",
    description: str | None = None,
    include_reverse: bool = True,
    force_reverse: bool | None = None,
) -> int:
    parser = build_parser(prog=prog, description=description, include_reverse=include_reverse)
    args = parser.parse_args(argv)

    reverse = force_reverse if force_reverse is not None else getattr(args, "reverse", False)
    if args.clipboard:
        if args.input is not None or args.output is not None:
            parser.error("--clipboard cannot be combined with input or output paths.")
        try:
            write_clipboard_text(transform_text(read_clipboard_text(), reverse=reverse))
        except RuntimeError as exc:
            sys.stderr.write(f"{exc}\n")
            return 1
        return 0

    if args.input is None:
        parser.error("the following arguments are required: input")

    input_path = Path(args.input).expanduser().resolve()
    converted = convert_tex_file(input_path, reverse=reverse)
    output_path = Path(args.output).expanduser().resolve() if args.output else input_path

    if output_path == input_path and not args.no_backup:
        backup_file(input_path, args.backup_dir)

    write_tex_file(converted, output_path)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
