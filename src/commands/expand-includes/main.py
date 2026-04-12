#!/usr/bin/env python3
"""CLI for recursively expanding LaTeX include directives."""

from __future__ import annotations

from pathlib import Path
import argparse
import sys

from lib.backup import backup_file
from lib.latex import expand_includes, write_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="expand-includes",
        description="Recursively expand \\input{...} and \\include{...} references.",
    )
    parser.add_argument("input", help="Root .tex file to flatten.")

    destination = parser.add_mutually_exclusive_group()
    destination.add_argument("-o", "--output", help="Write expanded output to this path.")
    destination.add_argument(
        "--in-place",
        action="store_true",
        help="Overwrite the input file with the expanded document.",
    )

    parser.add_argument(
        "-B",
        "--no-backup",
        action="store_true",
        help="Do not create a backup before overwriting a file.",
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
    flattened = expand_includes(input_path)

    if args.in_place:
        if not args.no_backup:
            backup_file(input_path, args.backup_dir)
        write_text(input_path, flattened)
        return 0

    if args.output:
        output_path = Path(args.output).expanduser().resolve()
        if output_path == input_path and not args.no_backup:
            backup_file(input_path, args.backup_dir)
        write_text(output_path, flattened)
        return 0

    sys.stdout.write(flattened)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
