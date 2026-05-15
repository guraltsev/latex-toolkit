#!/usr/bin/env python3
"""CLI for recursively expanding LaTeX include directives."""

from __future__ import annotations

from pathlib import Path
import argparse

from latex_toolkit.lib.backup import DEFAULT_BACKUP_DIR, backup_file
from latex_toolkit.lib.core import TexFile, write_tex_file
from latex_toolkit.lib.latex import expand_includes
from latex_toolkit.lib.logging_config import run_clipboard_transform, run_command



def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser.

    Returns
    -------
    argparse.ArgumentParser
        Parser configured for recursive include expansion.
    """

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

    Raises
    ------
    ValueError
        Expansion requires filename metadata and cannot proceed.
    FileNotFoundError
        A referenced include target cannot be resolved.
    latex_toolkit.lib.latex.IncludeCycleError
        Include expansion encounters a recursive include cycle.
    """

    root_dir = Path.cwd() if base_dir is None else Path(base_dir).expanduser().resolve()
    clipboard_source = TexFile(code=text, filename=root_dir / "__clipboard__.tex")
    return expand_includes(clipboard_source).code


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
