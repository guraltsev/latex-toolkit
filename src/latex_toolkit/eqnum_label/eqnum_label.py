r"""Normalize equation-label placement in display math.

The ``transform_text(...)`` API makes adjacent equation-number and label macros
space-separated in parsed display math. In a ``\[...\]`` or ``equation``
display, one label moves immediately after the opening delimiter. In an
align-family environment, a row label moves to its own line after that row's
terminating ``\\``.

Usage and API
-------------
Call ``transform_text(...)`` from Python, or use ``main(...)`` for file,
clipboard, and standard-stream workflows.

Implementation Approach
-----------------------
The module uses parsed display spans to limit edits to math and rewrites each
selected body independently. It treats an adjacent ``\eqnum \label`` pair as
one label unit, so the same placement rules apply when ``\eqnum`` is absent.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any

from latex_toolkit.lib.backup import backup_file
from latex_toolkit.lib.dependencies import DependencyManager
from latex_toolkit.lib.streams import configure_utf8_standard_streams


# These display environments can contain labels. Equation variants have one
# equation number, while align variants assign labels to individual rows.
_DISPLAY_ENVIRONMENTS = frozenset(
    {
        "displaymath", "equation", "equation*", "align", "align*", "alignat",
        "alignat*", "flalign", "flalign*", "gather", "gather*", "multline",
        "multline*", "split",
    }
)
_ALIGN_ENVIRONMENTS = frozenset(
    {"align", "align*", "alignat", "alignat*", "flalign", "flalign*"}
)


def transform_text(source: str) -> str:
    r"""Normalize adjacent ``\eqnum`` and ``\label`` macros in display math.

    A single label moves to the first line of a parsed ``\[...\]``,
    ``equation``, or ``equation*`` display. In align-family environments, a
    label written before a row terminator moves to its own following line. An
    adjacent ``\eqnum`` remains attached to its label when present.

    Parameters
    ----------
    source : str
        LaTeX source in complete-document or fragment form.

    Returns
    -------
    str
        Source with eligible equation-number label pairs canonicalized.

    Examples
    --------
    Basic usage:

    >>> transform_text("\\begin{equation}\\nx=1 \\label{eq:x}\\n\\end{equation}")
    '\\begin{equation}\\n\\label{eq:x}\\nx=1\\n\\end{equation}'
    """
    if not source:
        return source

    nodes = _parse(source)
    if nodes is None:
        return source
    document_bodies = [
        node.nodelist
        for node in nodes
        if type(node).__name__ == "LatexEnvironmentNode"
        and node.environmentname == "document"
    ]
    scopes = document_bodies or [nodes]

    # Collect non-overlapping display bodies before applying source-offset edits.
    ranges: list[tuple[int, int, str]] = []
    for scope in scopes:
        _collect_display_ranges(scope, source, ranges)
    return _apply_ranges(source, ranges)


def _collect_display_ranges(
    nodes: Iterable[Any], source: str, ranges: list[tuple[int, int, str]]
) -> None:
    """Collect display-body spans, marking their label-placement policy."""
    for node in nodes:
        node_type = type(node).__name__
        if node_type == "LatexEnvironmentNode":
            environment = node.environmentname
            content = getattr(node, "nodelist", None)
            if environment in _DISPLAY_ENVIRONMENTS and content is not None:
                if environment in {"equation", "equation*"}:
                    placement = "top"
                elif environment in _ALIGN_ENVIRONMENTS:
                    placement = "align"
                else:
                    placement = "preserve"
                ranges.append(
                    (content.pos, content.pos_end, placement)
                )
                continue
        elif node_type == "LatexMathNode":
            content = getattr(node, "nodelist", None)
            text = source[node.pos : node.pos_end]
            if content is not None and text.startswith(r"\[") and text.endswith(r"\]"):
                ranges.append((content.pos, content.pos_end, "top"))
                continue

        _collect_display_ranges(getattr(node, "nodelist", ()) or (), source, ranges)
        for argument in getattr(getattr(node, "nodeargd", None), "argnlist", ()) or ():
            if argument is not None:
                _collect_display_ranges((argument,), source, ranges)


def _apply_ranges(source: str, ranges: Iterable[tuple[int, int, str]]) -> str:
    """Apply independently rendered display-body edits from right to left."""
    transformed = source
    for start, end, placement in sorted(ranges, reverse=True):
        body = source[start:end]
        normalized = _normalize_pairs(body)
        if placement == "top":
            normalized = _move_single_label_to_top(normalized, _newline(source))
        elif placement == "align":
            normalized = _place_align_labels(normalized, _newline(source))
        transformed = transformed[:start] + normalized + transformed[end:]
    return transformed


def _normalize_pairs(body: str) -> str:
    """Make real adjacent equation-number label pairs use one separating space."""
    pattern = re.compile(r"\\eqnum[ \t\r\n]*\\label[ \t\r\n]*\{([^{}\r\n]*)\}")
    edits = [
        (match.start(), match.end(), rf"\eqnum \label{{{match.group(1)}}}")
        for match in pattern.finditer(body)
        if not _is_in_comment(body, match.start())
    ]
    return _apply_edits(body, edits)


def _move_single_label_to_top(body: str, newline: str) -> str:
    """Move one real label unit to the first line of a single-equation body."""
    pattern = re.compile(r"(?:\\eqnum )?\\label\{[^{}\r\n]*\}")
    matches = [
        match for match in pattern.finditer(body) if not _is_in_comment(body, match.start())
    ]
    if len(matches) != 1:
        return body

    match = matches[0]
    label = match.group()

    # Remove a dedicated label line as a unit so it cannot leave a blank line.
    line_start = body.rfind("\n", 0, match.start()) + 1
    line_end = body.find("\n", match.end())
    if line_end == -1:
        line_end = len(body)
    if body[line_start:match.start()].strip() or body[match.end():line_end].strip():
        # Drop padding that only separated an inline label from its formula.
        inline_start = match.start()
        while inline_start > line_start and body[inline_start - 1] in " \t":
            inline_start -= 1
        without_label = body[:inline_start] + body[match.end() :]
    else:
        after_line = line_end + 1 if line_end < len(body) else line_end
        without_label = body[:line_start] + body[after_line:]
    return newline + label + without_label


def _place_align_labels(body: str, newline: str) -> str:
    """Put labels before align row terminators onto their own following lines."""
    label = r"(?:\\eqnum )?\\label\{[^{}\r\n]*\}"
    before_terminator = re.compile(
        rf"(?m)^(?P<row>[^\r\n%]*?)(?P<gap>[ \t]*)(?P<label>{label})"
        r"[ \t]*(?P<terminator>\\\\(?:\[[^\r\n]*\])?)[ \t]*(?=\r?$)"
    )

    # A label at the end of a row belongs after its terminator, not in its math.
    def move_after_terminator(match: re.Match[str]) -> str:
        if _is_in_comment(body, match.start("label")):
            return match.group()
        return (
            f"{match.group('row')}{match.group('gap')}{match.group('terminator')}"
            f"{newline}{match.group('label')}"
        )

    return before_terminator.sub(move_after_terminator, body)


def _is_in_comment(source: str, position: int) -> bool:
    """Return whether a position is after an unescaped percent on its line."""
    line_start = source.rfind("\n", 0, position) + 1
    for index in range(line_start, position):
        if source[index] != "%":
            continue
        backslashes = 0
        cursor = index - 1
        while cursor >= line_start and source[cursor] == "\\":
            backslashes += 1
            cursor -= 1
        if backslashes % 2 == 0:
            return True
    return False


def _apply_edits(source: str, edits: Iterable[tuple[int, int, str]]) -> str:
    """Apply non-overlapping text edits in descending source order."""
    transformed = source
    for start, end, replacement in sorted(edits, reverse=True):
        transformed = transformed[:start] + replacement + transformed[end:]
    return transformed


def _newline(source: str) -> str:
    """Return the source's dominant physical-line convention."""
    return "\r\n" if "\r\n" in source else "\n"


def _parse(source: str) -> Any | None:
    """Parse source, returning ``None`` when parser spans are unsafe."""
    RUNTIME_DEPENDENCIES.require("pylatexenc.latexnodes.parsers")
    from pylatexenc.latexnodes.parsers import LatexGeneralNodesParser
    from pylatexenc.latexwalker import LatexWalker

    nodes, _ = LatexWalker(source).parse_content(LatexGeneralNodesParser())
    if nodes is None:
        return None
    return nodes


def _process_file(input_path: Path, output_path: Path) -> Path:
    """Transform one UTF-8 LaTeX file and write a separate UTF-8 result."""
    source = input_path.read_text(encoding="utf-8")
    output_path.write_text(transform_text(source), encoding="utf-8")
    return output_path


def main(argv: Sequence[str] | None = None) -> int:
    """Run equation-number label normalization in file, clipboard, or stdin mode."""
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.input_file is None and not args.clipboard and not args.stdin:
        args.clipboard = True
    selected_inputs = sum((args.input_file is not None, args.clipboard, args.stdin))
    if selected_inputs != 1:
        parser.error("provide an input file, --clipboard, or --stdin")
    if (args.clipboard or args.stdin) and args.output_file is not None:
        parser.error("--output cannot be used with --clipboard or --stdin")

    if args.clipboard:
        _transform_clipboard()
        return 0
    if args.stdin:
        configure_utf8_standard_streams()
        sys.stdout.write(transform_text(sys.stdin.read()))
        return 0

    if args.output_file is None and not args.no_backup:
        backup_file(args.input_file)
    output_path = args.output_file or args.input_file
    _process_file(args.input_file, output_path)
    print(f"Transformed file written to: {output_path}")
    return 0


RUNTIME_DEPENDENCIES = DependencyManager(
    {
        "pylatexenc.latexnodes.parsers": "pylatexenc>=3.0a33",
        "pyperclip": "pyperclip>=1.9",
    }
)


def _build_parser() -> argparse.ArgumentParser:
    """Build the interface for file, clipboard, and standard-stream workflows."""
    parser = argparse.ArgumentParser(description="Normalize \\eqnum equation labels.")
    parser.add_argument("input_file", nargs="?", type=Path, help="UTF-8 LaTeX file")
    parser.add_argument(
        "-o", "--output", "--output-file", dest="output_file", type=Path,
        help="destination path; preserves INPUT and skips its backup",
    )
    parser.add_argument(
        "-B", "--no-backup", action="store_true", help="overwrite INPUT without a backup"
    )
    parser.add_argument("--clipboard", action="store_true", help="transform the clipboard")
    parser.add_argument("--stdin", action="store_true", help="read stdin and write stdout")
    return parser


def _transform_clipboard() -> None:
    """Transform nonempty clipboard text and copy it back only on success."""
    pyperclip = RUNTIME_DEPENDENCIES.require("pyperclip")
    source = pyperclip.paste()
    if not source.strip():
        print("Clipboard is empty; nothing was changed.")
        return
    pyperclip.copy(transform_text(source))
    print("Normalized equation labels written back to the clipboard.")


if __name__ == "__main__":
    raise SystemExit(main())
