#!/usr/bin/env python3
"""CLI for converting between ``equation`` and ``\\[\\eqnum ... \\]``."""

from __future__ import annotations

from pathlib import Path
import argparse

from latex_toolkit.lib.backup import DEFAULT_BACKUP_DIR, backup_file
from latex_toolkit.lib.core import write_tex_file
from latex_toolkit.lib.logging_config import run_clipboard_transform, run_command
from .transform import convert_tex_file, convert_text

# This command overwrites source files unless output or clipboard mode is used.
OVERWRITES_SOURCE_TEX = True


def build_parser(
    *,
    prog: str = "eqn2dmath-eqnum",
    description: str | None = None,
    include_reverse: bool = True,
) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=prog,
        description=(
            description
            or (
                "Rewrite equation environments as \\[\\eqnum ... \\]. "
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
                "Rewrite \\[\\eqnum ... \\] blocks as equation environments instead. "
                "Plain display-math blocks are left untouched."
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
    """Convert ``equation`` and ``\\[\\eqnum ... \\]`` in ``text``.

    Parameters
    ----------
    text : str
        LaTeX source text to transform.
    reverse : bool
        ``False`` rewrites numbered equations as ``\\[\\eqnum ... \\]``.
        ``True`` rewrites standalone ``\\eqnum`` display math to equations.

    Returns
    -------
    str
        Converted source text.
    """

    return convert_text(text, reverse=reverse)


def main(
    argv: list[str] | None = None,
    *,
    prog: str = "eqn2dmath-eqnum",
    description: str | None = None,
    include_reverse: bool = True,
    force_reverse: bool | None = None,
) -> int:
    def run() -> int:
        parser = build_parser(prog=prog, description=description, include_reverse=include_reverse)
        args = parser.parse_args(argv)

        reverse = force_reverse if force_reverse is not None else getattr(args, "reverse", False)
        if args.clipboard:
            if args.input is not None or args.output is not None:
                parser.error("--clipboard cannot be combined with input or output paths.")
            run_clipboard_transform(
                prog,
                lambda text: transform_text(text, reverse=reverse),
            )
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

    return run_command(prog, run)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
