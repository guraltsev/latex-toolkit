#!/usr/bin/env python3
"""CLI for recursively expanding LaTeX include directives."""

from __future__ import annotations

from pathlib import Path
import argparse

from lib.backup import DEFAULT_BACKUP_DIR, backup_file
from lib.core import TexFile, write_tex_file
from lib.latex import expand_includes
from lib.logging_config import run_clipboard_transform, run_command

# This command overwrites source files unless output or clipboard mode is used.
OVERWRITES_SOURCE_TEX = True


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="expand-includes",
        description=(
            "Recursively expand \\input{...}, \\include{...}, and subfiles commands. "
            "By default the input file is overwritten; use -o/--output to write elsewhere."
        ),
    )
    parser.add_argument("input", nargs="?", help="Root .tex file to flatten.")
    parser.add_argument(
        "--clipboard",
        action="store_true",
        help="Read LaTeX from the clipboard and replace it with expanded output.",
    )
    parser.add_argument(
        "-o",
        "--output",
        "--output-file",
        dest="output",
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
        default=DEFAULT_BACKUP_DIR,
        help="Relative or absolute directory for backups when overwriting. Default: %(default)s",
    )
    return parser


def transform_text(text: str, *, base_dir: str | Path | None = None) -> str:
    """Expand include directives in ``text`` and return flattened source.

    Parameters
    ----------
    text : str
        LaTeX source text to transform.
    base_dir : str, pathlib.Path, or None
        Directory used to resolve relative include targets. ``None`` resolves
        targets from the current working directory.

    Returns
    -------
    str
        Source text with supported include commands expanded.
    """

    root_dir = Path.cwd() if base_dir is None else Path(base_dir).expanduser().resolve()
    clipboard_source = TexFile(code=text, filename=root_dir / "__clipboard__.tex")
    return expand_includes(clipboard_source).code


def main(argv: list[str] | None = None) -> int:
    def run() -> int:
        parser = build_parser()
        args = parser.parse_args(argv)

        if args.clipboard:
            if args.input is not None or args.output is not None:
                parser.error("--clipboard cannot be combined with input or output paths.")
            run_clipboard_transform("expand-includes", transform_text)
            return 0

        if args.input is None:
            parser.error("the following arguments are required: input")

        input_path = Path(args.input).expanduser().resolve()
        expanded = expand_includes(input_path)
        output_path = Path(args.output).expanduser().resolve() if args.output else input_path

        if output_path == input_path and not args.no_backup:
            backup_file(input_path, args.backup_dir)

        write_tex_file(expanded, output_path)
        return 0

    return run_command("expand-includes", run)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
