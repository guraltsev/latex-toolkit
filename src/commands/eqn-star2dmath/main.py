#!/usr/bin/env python3
"""CLI for converting between ``equation*`` and plain display math."""

from __future__ import annotations

from pathlib import Path
import argparse

from lib.backup import backup_file
from lib.core import write_tex_file
from lib.equation_star_displaymath import convert_tex_file

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
    parser.add_argument("input", help="Input .tex file.")
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
        default=".lt-backup",
        help="Relative or absolute directory for backups when overwriting. Default: %(default)s",
    )
    return parser


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
    input_path = Path(args.input).expanduser().resolve()
    converted = convert_tex_file(input_path, reverse=reverse)
    output_path = Path(args.output).expanduser().resolve() if args.output else input_path

    if output_path == input_path and not args.no_backup:
        backup_file(input_path, args.backup_dir)

    write_tex_file(converted, output_path)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
