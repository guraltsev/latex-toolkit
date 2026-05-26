#!/usr/bin/env python3
"""CLI for formatting LaTeX with latexindent and the toolkit's bundled config."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import argparse
import shutil
import subprocess

from latex_toolkit.lib.backup import DEFAULT_BACKUP_DIR, backup_file
from latex_toolkit.lib.latex import read_text, write_text
from latex_toolkit.lib.logging_config import run_clipboard_transform, run_command


LATEXINDENT_EXECUTABLE_NAMES = ("latexindent", "latexindent.pl")


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser.

    Returns
    -------
    argparse.ArgumentParser
        Parser configured for latexindent-based formatting.
    """

    parser = argparse.ArgumentParser(
        prog="latex_indent",
        description=(
            "Format LaTeX with latexindent and the toolkit's bundled config. "
            "By default the input file is overwritten; use -o/--output to write elsewhere."
        ),
    )
    parser.add_argument("input", nargs="?", help="Input .tex file.")
    parser.add_argument(
        "--clipboard",
        action="store_true",
        help="Read LaTeX from the clipboard and replace it with formatted output.",
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


def transform_text(text: str) -> str:
    """Format LaTeX text with latexindent and the bundled local settings file.

    Parameters
    ----------
    text : str
        LaTeX source text to format.

    Returns
    -------
    str
        Source text formatted by ``latexindent``.

    Raises
    ------
    RuntimeError
        The latexindent executable cannot be found or exits with an error.
    """

    executable = _find_latexindent_executable()
    if executable is None:
        raise RuntimeError(
            "latexindent is not installed or not on PATH. "
            "Install latexindent to use latex_indent."
        )

    with TemporaryDirectory() as temp_dir:
        work = Path(temp_dir)
        input_path = work / "input.tex"

        # Run latexindent inside a temporary workspace so any auxiliary files it
        # chooses to emit stay out of the user's project tree.
        input_path.write_text(text, encoding="utf-8")
        command = [
            executable,
            "-m",
            "-l",
            str(_default_config_path()),
            str(input_path),
        ]
        completed = subprocess.run(
            command,
            cwd=str(work),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

    if completed.returncode != 0:
        raise RuntimeError(_format_process_failure("latexindent formatting failed", completed))
    return completed.stdout


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
            run_clipboard_transform("latex_indent", transform_text)
            return 0

        if args.input is None:
            parser.error("the following arguments are required: input")

        input_path = Path(args.input).expanduser().resolve()
        formatted = transform_text(read_text(input_path))
        output_path = Path(args.output).expanduser().resolve() if args.output else input_path

        if output_path == input_path and not args.no_backup:
            backup_file(input_path, args.backup_dir)

        write_text(output_path, formatted)
        return 0

    return run_command("latex_indent", run)


def _find_latexindent_executable() -> str | None:
    """Return the first latexindent executable available on ``PATH``."""

    for executable_name in LATEXINDENT_EXECUTABLE_NAMES:
        executable = shutil.which(executable_name)
        if executable is not None:
            return executable
    return None


def _default_config_path() -> Path:
    """Return the bundled latexindent configuration file path."""

    return Path(__file__).with_name("latexindent.yaml")


def _format_process_failure(message: str, completed: subprocess.CompletedProcess[str]) -> str:
    """Return a concise subprocess failure message."""

    details = (completed.stderr or completed.stdout).strip()
    if details:
        return f"{message}: {details}"
    return f"{message} with exit code {completed.returncode}."


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
