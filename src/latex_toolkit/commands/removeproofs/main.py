#!/usr/bin/env python3
"""CLI for removing proof environments and their contents from LaTeX text."""

from __future__ import annotations

from pathlib import Path
import argparse
import importlib.util
import subprocess
import sys

from latex_toolkit.lib.backup import DEFAULT_BACKUP_DIR, backup_file
from latex_toolkit.lib.latex import read_text, write_text
from latex_toolkit.lib.logging_config import run_clipboard_transform, run_command

# Install the parser dependency into a user-writable cache when it is missing.
PYLATEXENC_PACKAGE = "pylatexenc"


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser.

    Returns
    -------
    argparse.ArgumentParser
        Parser configured for proof-environment removal.
    """

    parser = argparse.ArgumentParser(
        prog="removeproofs",
        description=(
            "Remove proof environments and their contents from LaTeX. "
            "With no input or output paths, the command processes clipboard text."
        ),
    )
    parser.add_argument("input", nargs="?", help="Input .tex file.")
    parser.add_argument(
        "--clipboard",
        action="store_true",
        help="Read LaTeX from the clipboard and replace it with processed output.",
    )
    parser.add_argument(
        "-o",
        "--output",
        "--output-file",
        dest="output",
        help="Write processed output to this path instead of overwriting the input file.",
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
    """Remove proof environments and their contents from ``text``.

    Parameters
    ----------
    text : str
        LaTeX source text to transform.

    Returns
    -------
    str
        Source text with ``proof`` and ``proof*`` environments removed.

    Notes
    -----
    The first call installs ``pylatexenc`` into a user-writable cache when the
    dependency is not already available.
    """

    ensure_pylatexenc()
    return _remove_proof_environments(text)


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

        # Treat a missing input path as clipboard mode so the Windows launcher
        # works on copied LaTeX without an extra flag.
        use_clipboard = args.clipboard or (args.input is None and args.output is None)

        if use_clipboard:
            if args.input is not None or args.output is not None:
                parser.error("--clipboard cannot be combined with input or output paths.")
            run_clipboard_transform("removeproofs", transform_text)
            return 0

        if args.input is None:
            parser.error("the following arguments are required: input")

        input_path = Path(args.input).expanduser().resolve()
        processed = transform_text(read_text(input_path))
        output_path = Path(args.output).expanduser().resolve() if args.output else input_path

        if output_path == input_path and not args.no_backup:
            backup_file(input_path, args.backup_dir)

        write_text(output_path, processed)
        return 0

    return run_command("removeproofs", run)


def ensure_pylatexenc() -> None:
    """Ensure that ``pylatexenc`` is importable, installing it when needed.

    Returns
    -------
    None
        The dependency is importable after the function returns.

    Raises
    ------
    RuntimeError
        The dependency cannot be imported or installed successfully.
    """

    install_root = _pylatexenc_install_root()
    if str(install_root) not in sys.path:
        sys.path.insert(0, str(install_root))

    if importlib.util.find_spec(PYLATEXENC_PACKAGE) is not None:
        return

    install_root.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--disable-pip-version-check",
        "--no-warn-script-location",
        "--upgrade",
        "--target",
        str(install_root),
        PYLATEXENC_PACKAGE,
    ]
    completed = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(_format_process_failure(f"could not install {PYLATEXENC_PACKAGE}", completed))

    if importlib.util.find_spec(PYLATEXENC_PACKAGE) is None:
        raise RuntimeError(
            f"{PYLATEXENC_PACKAGE} was installed into {install_root}, but the package is still not importable."
        )


def _remove_proof_environments(text: str) -> str:
    """Return ``text`` with proof-environment spans removed."""

    if not text.strip():
        return text

    LatexWalker = _load_latexwalker()
    try:
        nodes, _, _ = LatexWalker(text).get_latex_nodes()
    except Exception as exc:  # pragma: no cover - dependent parser failure path
        raise RuntimeError(f"could not parse LaTeX: {exc}") from exc

    spans = _merge_spans(_collect_proof_spans(nodes))
    if not spans:
        return text

    pieces: list[str] = []
    cursor = 0
    for start, end in spans:
        pieces.append(text[cursor:start])
        cursor = end
    pieces.append(text[cursor:])
    return "".join(pieces)


def _collect_proof_spans(nodes: object) -> list[tuple[int, int]]:
    """Collect proof-environment spans from a parsed node tree."""

    spans: list[tuple[int, int]] = []
    for node in _iter_nodes(nodes):
        if not _is_proof_environment(node):
            continue
        start = getattr(node, "pos", None)
        end = getattr(node, "pos_end", None)
        if isinstance(start, int) and isinstance(end, int) and start <= end:
            spans.append((start, end))
    return spans


def _iter_nodes(value: object) -> object:
    """Yield nodes from nested node lists and argument lists."""

    if value is None:
        return

    if isinstance(value, (list, tuple)):
        for item in value:
            yield from _iter_nodes(item)
        return

    yield value

    nodelist = getattr(value, "nodelist", None)
    if nodelist is not None:
        yield from _iter_nodes(nodelist)

    nodeargd = getattr(value, "nodeargd", None)
    if nodeargd is not None:
        yield from _iter_nodes(getattr(nodeargd, "argnlist", None))


def _is_proof_environment(node: object) -> bool:
    """Return whether ``node`` represents a proof environment."""

    environment_name = getattr(node, "environmentname", None)
    if environment_name is None:
        environment_name = getattr(node, "envname", None)
    return environment_name in {"proof", "proof*"}


def _merge_spans(spans: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Return sorted, non-overlapping proof spans."""

    if not spans:
        return []

    merged: list[tuple[int, int]] = [spans[0]]
    for start, end in sorted(spans[1:]):
        previous_start, previous_end = merged[-1]
        if start <= previous_end:
            merged[-1] = (previous_start, max(previous_end, end))
        else:
            merged.append((start, end))
    return merged


def _load_latexwalker():
    """Import and return ``LatexWalker`` after ensuring the dependency exists."""

    ensure_pylatexenc()
    from pylatexenc.latexwalker import LatexWalker

    return LatexWalker


def _pylatexenc_install_root() -> Path:
    """Return the user cache directory used for the ``pylatexenc`` install."""

    return Path.home() / ".latex-toolkit" / "pylatexenc"


def _format_process_failure(message: str, completed: subprocess.CompletedProcess[str]) -> str:
    """Return a concise subprocess failure message."""

    details = (completed.stderr or completed.stdout).strip()
    if details:
        return f"{message}: {details}"
    return f"{message} with exit code {completed.returncode}."


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
