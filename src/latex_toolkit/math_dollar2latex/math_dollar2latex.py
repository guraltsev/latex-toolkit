r"""This module converts dollar-delimited LaTeX math to command-style delimiters.

The ``transform_text(...)`` API accepts fragments or complete documents. Inline
``$...$`` becomes ``\(...\)``, and display ``$$...$$`` becomes ``\[...\]``.
For complete documents, only document bodies are transformed.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from latex_toolkit.lib.dependencies import DependencyManager
from latex_toolkit.lib.backup import backup_file
from latex_toolkit.lib.streams import configure_utf8_standard_streams


def transform_text(source: str, *, reverse: bool = False) -> str:
    r"""Convert math delimiters while preserving math contents exactly.

    Complete documents are transformed only inside top-level ``document``
    environments. Inputs without a document environment are treated as LaTeX
    fragments. Set ``reverse`` to convert command-style delimiters to dollar
    delimiters for the reverse command in this command family.

    Parameters
    ----------
    source : str
        LaTeX source in complete-document or fragment form.
    reverse : bool, optional
        Convert ``\(...\)`` and ``\[...\]`` to dollar delimiters when true.

    Returns
    -------
    str
        Source with recognized target math delimiters replaced.

    Examples
    --------
    Basic usage:

    >>> transform_text("Inline $x$ and display $$y$$.")
    'Inline \\(x\\) and display \\[y\\].'

    Reverse conversion:

    >>> transform_text(r"Inline \(x\) and display \[y\].", reverse=True)
    'Inline $x$ and display $$y$$.'
    """
    if not source:
        return source

    nodes = _parse(source)
    if nodes is None:
        return source

    # Preserve complete-document preambles, while treating standalone input as
    # a fragment whose full contents belong to the transformation scope.
    document_bodies = [
        node.nodelist
        for node in nodes
        if type(node).__name__ == "LatexEnvironmentNode"
        and node.environmentname == "document"
    ]
    scopes = document_bodies or [nodes]

    # Derive edits from parsed math nodes so escaped dollars and literal text
    # cannot be mistaken for delimiters. Edits affect delimiters only.
    edits: list[tuple[int, int, str]] = []
    for scope in scopes:
        _collect_delimiter_edits(source, scope, reverse, edits)

    transformed = source
    for start, end, replacement in sorted(set(edits), reverse=True):
        transformed = transformed[:start] + replacement + transformed[end:]
    return transformed


def _process_file(input_path: Path, output_path: Path, *, reverse: bool = False) -> Path:
    """Transform one UTF-8 LaTeX file and write a separate UTF-8 result.

    Parameters
    ----------
    input_path : pathlib.Path
        Source file to read without modifying.
    output_path : pathlib.Path
        Destination to create or replace with transformed source.
    reverse : bool, optional
        Apply the reverse delimiter conversion when true.

    Returns
    -------
    pathlib.Path
        The destination supplied by the caller.

    Raises
    ------
    OSError
        The source cannot be read or the destination cannot be written.
    """
    # Finish reading and transforming before opening the destination so an
    # identical input and output path cannot truncate the source prematurely.
    source = input_path.read_text(encoding="utf-8")
    transformed = transform_text(source, reverse=reverse)
    output_path.write_text(transformed, encoding="utf-8")
    return output_path


def main(argv: Sequence[str] | None = None) -> int:
    """Run conversion in file, clipboard, or standard-stream mode.

    With no arguments, the command transforms the system clipboard.

    Parameters
    ----------
    argv : sequence of str, optional
        Command-line arguments without the executable name.

    Returns
    -------
    int
        Process exit status; zero indicates success.

    Raises
    ------
    SystemExit
        Arguments select incompatible input or output modes.
    """
    return _run_command(argv, reverse=False)


# Parsing and source transformation


def _parse(source: str) -> Any | None:
    """Parse source, returning ``None`` when node spans are incomplete."""
    RUNTIME_DEPENDENCIES.require("pylatexenc.latexnodes.parsers")
    from pylatexenc.latexnodes.parsers import LatexGeneralNodesParser
    from pylatexenc.latexwalker import LatexWalker

    nodes, _ = LatexWalker(source).parse_content(LatexGeneralNodesParser())
    if nodes is None:
        return None

    # Tolerant parsing may produce incomplete nodes whose source boundaries are
    # unsafe to edit. Leave such input unchanged.
    pending = list(nodes)
    visited: set[int] = set()
    while pending:
        node = pending.pop()
        if id(node) in visited:
            continue
        visited.add(id(node))
        if getattr(node, "pos", None) is None or getattr(node, "pos_end", None) is None:
            return None
        children = getattr(node, "nodelist", None)
        if children is not None:
            pending.extend(children)
        arguments = getattr(getattr(node, "nodeargd", None), "argnlist", ()) or ()
        pending.extend(argument for argument in arguments if argument is not None)
    return nodes


def _collect_delimiter_edits(
    source: str,
    nodes: Any,
    reverse: bool,
    edits: list[tuple[int, int, str]],
) -> None:
    """Collect delimiter-only edits from parsed math nodes in one scope."""
    for node in nodes:
        if type(node).__name__ == "LatexMathNode":
            math_source = source[node.pos : node.pos_end]
            inline = getattr(node, "displaytype", None) == "inline"
            if reverse:
                delimiters = (
                    (r"\(", r"\)", "$", "$") if inline else (r"\[", r"\]", "$$", "$$")
                )
            else:
                delimiters = (
                    ("$", "$", r"\(", r"\)") if inline else ("$$", "$$", r"\[", r"\]")
                )
            opening, closing, new_opening, new_closing = delimiters
            if math_source.startswith(opening) and math_source.endswith(closing):
                edits.append((node.pos, node.pos + len(opening), new_opening))
                edits.append((node.pos_end - len(closing), node.pos_end, new_closing))
            continue

        children = getattr(node, "nodelist", ()) or ()
        _collect_delimiter_edits(source, children, reverse, edits)
        arguments = getattr(getattr(node, "nodeargd", None), "argnlist", ()) or ()
        for argument in arguments:
            if argument is not None:
                _collect_delimiter_edits(source, (argument,), reverse, edits)


# Dependency and command boundaries


# Keep only this command's dependency declarations near its command boundary.
RUNTIME_DEPENDENCIES = DependencyManager(
    {
        "pylatexenc.latexnodes.parsers": "pylatexenc>=3.0a33",
        "pyperclip": "pyperclip>=1.9",
    }
)


def _run_command(argv: Sequence[str] | None, *, reverse: bool) -> int:
    """Run either direction with command-specific labels and behavior."""
    parser = _build_parser(reverse)
    args = parser.parse_args(argv)
    if args.input_file is None and not args.clipboard and not args.stdin:
        args.clipboard = True
    selected_inputs = sum((args.input_file is not None, args.clipboard, args.stdin))
    if selected_inputs != 1:
        parser.error("provide an input file, --clipboard, or --stdin")
    if (args.clipboard or args.stdin) and args.output_file is not None:
        parser.error("--output cannot be used with --clipboard or --stdin")

    if args.clipboard:
        _transform_clipboard(reverse)
        return 0
    if args.stdin:
        configure_utf8_standard_streams()
        sys.stdout.write(transform_text(sys.stdin.read(), reverse=reverse))
        return 0

    if args.output_file is None and not args.no_backup:
        backup_file(args.input_file)
    output_path = args.output_file or args.input_file
    _process_file(args.input_file, output_path, reverse=reverse)
    print(f"Transformed file written to: {output_path}")
    return 0


def _build_parser(reverse: bool) -> argparse.ArgumentParser:
    """Build the command-line interface for one conversion direction."""
    description = (
        r"Convert \(...\) and \[...\] to $...$ and $$...$$."
        if reverse
        else r"Convert $...$ and $$...$$ to \(...\) and \[...\]."
    )
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("input_file", nargs="?", type=Path, help="UTF-8 LaTeX file")
    parser.add_argument(
        "-o",
        "--output",
        "--output-file",
        dest="output_file",
        type=Path,
        help="destination path; preserves INPUT and skips its backup",
    )
    parser.add_argument(
        "-B", "--no-backup", action="store_true", help="overwrite INPUT without a backup"
    )
    parser.add_argument(
        "--clipboard",
        action="store_true",
        help="transform the system clipboard instead of a file",
    )
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="read UTF-8 LaTeX from stdin and write the result to stdout",
    )
    return parser


def _default_output_path(input_path: Path, reverse: bool) -> Path:
    """Return a sibling path labeled for the selected conversion direction."""
    suffix = input_path.suffix or ".tex"
    stem = input_path.stem if input_path.suffix else input_path.name
    label = "dollar_math" if reverse else "latex_delimiters"
    return input_path.with_name(f"{stem}_{label}{suffix}")


def _transform_clipboard(reverse: bool) -> None:
    """Transform nonempty clipboard text and copy it back only on success."""
    pyperclip = RUNTIME_DEPENDENCIES.require("pyperclip")
    source = pyperclip.paste()
    if not source.strip():
        print("Clipboard is empty; nothing was changed.")
        return
    pyperclip.copy(transform_text(source, reverse=reverse))
    print("Converted LaTeX written back to the clipboard.")


if __name__ == "__main__":
    raise SystemExit(main())
