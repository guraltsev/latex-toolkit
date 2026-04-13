#!/usr/bin/env python3
"""CLI for recursively expanding LaTeX include directives."""

from __future__ import annotations

from pathlib import Path
import argparse

from lib.backup import backup_file
from lib.core import write_tex_file
from lib.latex import expand_includes

OVERWRITES_SOURCE_TEX = True


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="expand-includes",
        description=(
            "Recursively expand \\input{...}, \\include{...}, and subfiles commands. "
            "By default the input file is overwritten; use -o/--output to write elsewhere."
        ),
    )
    parser.add_argument("input", help="Root .tex file to flatten.")
    parser.add_argument(
        "-o",
        "--output",
        help="Write expanded output to this path instead of overwriting the input file.",
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


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    input_path = Path(args.input).expanduser().resolve()
    expanded = expand_includes(input_path)
    output_path = Path(args.output).expanduser().resolve() if args.output else input_path

    if output_path == input_path and not args.no_backup:
        backup_file(input_path, args.backup_dir)

    write_tex_file(expanded, output_path)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
