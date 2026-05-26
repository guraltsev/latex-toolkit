#!/usr/bin/env python3
"""CLI for formatting LaTeX with latexindent and the toolkit's bundled config."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import argparse
import os
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

    preferred_line_ending = _preferred_line_ending(text)
    normalized_text = _normalize_line_endings(text)

    with TemporaryDirectory() as temp_dir:
        work = Path(temp_dir)
        input_path = work / "input.tex"

        # Run latexindent inside a temporary workspace so any auxiliary files it
        # chooses to emit stay out of the user's project tree.
        input_path.write_text(normalized_text, encoding="utf-8")
        command = [
            executable,
            "-m",
            f"-l={_default_config_path()}",
            str(input_path),
        ]
        completed = subprocess.run(
            command,
            cwd=str(work),
            env=_isolated_latexindent_env(work),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            check=False,
        )

    if completed.returncode != 0:
        raise RuntimeError(_format_process_failure("latexindent formatting failed", completed))

    # Keep the wrapper transport-only: normalize line endings for latexindent,
    # then restore the caller's original convention on the formatter output.
    normalized_output = _normalize_line_endings(completed.stdout)
    return _apply_line_ending(normalized_output, preferred_line_ending)


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


def _normalize_line_endings(text: str) -> str:
    """Return text with all line endings normalized to ``\\n``."""

    return text.replace("\r\n", "\n").replace("\r", "\n")


def _preferred_line_ending(text: str) -> str:
    """Return the dominant line ending style from the original input text."""

    if "\r\n" in text:
        return "\r\n"
    if "\r" in text:
        return "\r"
    return "\n"


def _apply_line_ending(text: str, line_ending: str) -> str:
    """Return text rewritten to the requested line-ending style."""

    if line_ending == "\n":
        return text
    return text.replace("\n", line_ending)


def _isolated_latexindent_env(work: Path) -> dict[str, str]:
    """Return a process environment that ignores user latexindent config files."""

    env = os.environ.copy()
    isolated_home = str(work)

    # Keep latexindent deterministic by preventing user-scoped config discovery
    # from changing indentation or enabling line-break rewrites.
    for variable in ("HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "XDG_CONFIG_HOME"):
        env[variable] = isolated_home
    return env


def _format_process_failure(message: str, completed: subprocess.CompletedProcess[str]) -> str:
    """Return a concise subprocess failure message."""

    details = (completed.stderr or completed.stdout).strip()
    if details:
        return f"{message}: {details}"
    return f"{message} with exit code {completed.returncode}."


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
