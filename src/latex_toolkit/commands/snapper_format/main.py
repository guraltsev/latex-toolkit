#!/usr/bin/env python3
"""CLI for formatting LaTeX prose with snapper semantic line breaks."""

from __future__ import annotations

from pathlib import Path
import argparse
import re
import subprocess
import sys

from latex_toolkit.lib.backup import DEFAULT_BACKUP_DIR, backup_file
from latex_toolkit.lib.latex import read_text, write_text
from latex_toolkit.lib.logging_config import run_clipboard_transform, run_command


SNAPPER_PACKAGE = "snapper-fmt"
SNAPPER_EXECUTABLE_NAMES = ("snapper.exe", "snapper.cmd", "snapper.bat", "snapper")

# Snapper's LaTeX parser treats material before ``\begin{document}`` as
# structure, so snippets are wrapped before formatting and unwrapped afterward.
BEGIN_DOCUMENT_RE = re.compile(r"\\begin\s*\{document\}")
DOCUMENT_BEGIN = r"\begin{document}"
DOCUMENT_END = r"\end{document}"


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser.

    Returns
    -------
    argparse.ArgumentParser
        Parser configured for snapper-based LaTeX formatting.
    """

    parser = argparse.ArgumentParser(
        prog="snapper_format",
        description=(
            "Format LaTeX prose with snapper semantic line breaks. "
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
        "--install",
        action="store_true",
        help="Download or refresh the local snapper-fmt runtime, then exit.",
    )
    parser.add_argument(
        "--max-width",
        type=int,
        default=0,
        help=(
            "Wrap sentences longer than this width after snapper splits them. "
            "The default, 0, keeps each sentence on one line."
        ),
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


def transform_text(text: str, *, max_width: int = 0) -> str:
    """Format LaTeX prose so each emitted line contains at most one sentence.

    Parameters
    ----------
    text : str
        LaTeX source text to transform.
    max_width : int
        Maximum width for wrapping long sentences after sentence splitting.
        ``0`` disables width wrapping.

    Returns
    -------
    str
        Source text formatted by the local ``snapper`` executable.

    Raises
    ------
    RuntimeError
        The local snapper executable cannot be found, installed, or run
        successfully.
    """

    snapper = ensure_snapper()
    snapper_input, wrapped_fragment = _snapper_input(text)
    command = [
        str(snapper),
        "--format",
        "latex",
        "--max-width",
        str(max_width),
    ]
    completed = subprocess.run(
        command,
        input=snapper_input,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(_format_process_failure("snapper formatting failed", completed))

    if wrapped_fragment:
        return _unwrap_snapper_output(completed.stdout)
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

        if args.max_width < 0:
            parser.error("--max-width must be zero or positive.")

        if args.install:
            if args.input is not None or args.output is not None or args.clipboard:
                parser.error("--install cannot be combined with input, output, or --clipboard.")
            install_snapper()
            return 0

        if args.clipboard:
            if args.input is not None or args.output is not None:
                parser.error("--clipboard cannot be combined with input or output paths.")
            run_clipboard_transform(
                "snapper_format",
                lambda text: transform_text(text, max_width=args.max_width),
            )
            return 0

        if args.input is None:
            parser.error("the following arguments are required: input")

        input_path = Path(args.input).expanduser().resolve()
        formatted = transform_text(read_text(input_path), max_width=args.max_width)
        output_path = Path(args.output).expanduser().resolve() if args.output else input_path

        if output_path == input_path and not args.no_backup:
            backup_file(input_path, args.backup_dir)

        write_text(output_path, formatted)
        return 0

    return run_command("snapper_format", run)


def ensure_snapper() -> Path:
    """Return the local snapper executable, installing it when missing.

    Returns
    -------
    pathlib.Path
        Path to the repository-local snapper executable.

    Raises
    ------
    RuntimeError
        Snapper cannot be installed or no executable is found afterward.
    """

    snapper = _find_snapper_executable()
    if snapper is not None:
        return snapper

    install_snapper()
    snapper = _find_snapper_executable()
    if snapper is None:
        raise RuntimeError(
            f"{SNAPPER_PACKAGE} installed into {_snapper_install_root()}, "
            "but no snapper executable was found."
        )
    return snapper


def install_snapper() -> None:
    """Install or refresh snapper-fmt inside the repository-local lib directory.

    Returns
    -------
    None
        The repository-local snapper installation is created or updated.

    Raises
    ------
    RuntimeError
        The pip install process exits with a nonzero status.
    """

    install_root = _snapper_install_root()
    install_root.mkdir(parents=True, exist_ok=True)

    # Install into a repository-local prefix so the command never depends on a
    # globally available snapper binary or mutates the user's Python install.
    command = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--disable-pip-version-check",
        "--no-warn-script-location",
        "--upgrade",
        "--ignore-installed",
        "--prefix",
        str(install_root),
        SNAPPER_PACKAGE,
    ]
    completed = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(_format_process_failure(f"could not install {SNAPPER_PACKAGE}", completed))


def _snapper_install_root() -> Path:
    """Return the repository-local snapper installation prefix."""

    command_file = Path(__file__).resolve()
    for parent in command_file.parents:
        if (parent / "pyproject.toml").is_file() and (parent / "src").is_dir():
            return parent / "src" / "latex_toolkit" / "lib" / "snapper-fmt"
    return command_file.parents[2] / "lib" / "snapper-fmt"


def _find_snapper_executable() -> Path | None:
    """Return a snapper executable from the local install prefix if present."""

    install_root = _snapper_install_root()
    candidate_dirs = (
        install_root / "Scripts",
        install_root / "bin",
        install_root,
    )
    for candidate_dir in candidate_dirs:
        for executable_name in SNAPPER_EXECUTABLE_NAMES:
            candidate = candidate_dir / executable_name
            if candidate.is_file():
                return candidate

    # Wheel layouts can vary across platforms, so fall back to a small bounded
    # search inside the dedicated install directory before reinstalling.
    if not install_root.exists():
        return None
    executable_names = set(SNAPPER_EXECUTABLE_NAMES)
    for candidate in install_root.rglob("snapper*"):
        if candidate.name in executable_names and candidate.is_file():
            return candidate
    return None


def _snapper_input(text: str) -> tuple[str, bool]:
    """Return LaTeX text that snapper should treat as document body."""

    if BEGIN_DOCUMENT_RE.search(text):
        return text, False

    line_ending = "\r\n" if "\r\n" in text else "\n"
    body = text
    if body and not body.endswith(("\n", "\r")):
        body += line_ending
    return f"{DOCUMENT_BEGIN}{line_ending}{body}{DOCUMENT_END}{line_ending}", True


def _unwrap_snapper_output(text: str) -> str:
    """Remove the temporary document wrapper from snapper output."""

    lines = text.splitlines(keepends=True)
    if lines and lines[0].strip() == DOCUMENT_BEGIN:
        lines = lines[1:]
    if lines and lines[-1].strip() == DOCUMENT_END:
        lines = lines[:-1]
    return "".join(lines)


def _format_process_failure(message: str, completed: subprocess.CompletedProcess[str]) -> str:
    """Return a concise subprocess failure message."""

    details = (completed.stderr or completed.stdout).strip()
    if details:
        return f"{message}: {details}"
    return f"{message} with exit code {completed.returncode}."


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
