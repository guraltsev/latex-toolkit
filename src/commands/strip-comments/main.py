#!/usr/bin/env python3
"""CLI for stripping LaTeX percent comments."""

from __future__ import annotations

from pathlib import Path
import argparse
import sys

from lib.backup import backup_file
from lib.latex import read_text, strip_comments_from_text, write_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="strip-comments",
        description="Remove LaTeX percent comments while preserving escaped percent signs.",
    )
    parser.add_argument("input", help="Input .tex file.")

    destination = parser.add_mutually_exclusive_group()
    destination.add_argument("-o", "--output", help="Write stripped output to this path.")
    destination.add_argument(
        "--in-place",
        action="store_true",
        help="Overwrite the input file with comments removed.",
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
    stripped = strip_comments_from_text(read_text(input_path))

    if args.in_place:
        if not args.no_backup:
            backup_file(input_path, args.backup_dir)
        write_text(input_path, stripped)
        return 0

    if args.output:
        output_path = Path(args.output).expanduser().resolve()
        if output_path == input_path and not args.no_backup:
            backup_file(input_path, args.backup_dir)
        write_text(output_path, stripped)
        return 0

    sys.stdout.write(stripped)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
