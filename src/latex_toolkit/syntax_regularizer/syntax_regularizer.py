r"""Regularize source layout without changing protected LaTeX regions.

Call ``transform_text(...)`` for fragments or complete documents. Inline math
is unwrapped unless it contains a comment, display delimiters are isolated on
source lines, and ordinary text indentation is removed while math, verbatim,
and table-like environments retain their layout.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any

from latex_toolkit.lib.dependencies import DependencyManager
from latex_toolkit.lib.backup import backup_file


def transform_text(source: str) -> str:
    r"""Regularize inline math, display math, and ordinary text indentation.

    Complete documents are transformed only inside top-level ``document``
    environments. Inputs without a document environment are treated as LaTeX
    fragments. Incomplete input that cannot be sliced safely is returned
    unchanged.

    Parameters
    ----------
    source : str
        LaTeX source in complete-document or fragment form.

    Returns
    -------
    str
        Source with regularized physical-line layout.

    Examples
    --------
    Basic usage:

    >>> transform_text("  Text with $1+1=\\n2$. ")
    'Text with $1+1=2$. '
    """
    if not source:
        return source

    nodes = _parse(source)
    if nodes is None:
        return source
    document_bodies = [
        (node.nodelist.pos, node.nodelist.pos_end)
        for node in nodes
        if type(node).__name__ == "LatexEnvironmentNode"
        and node.environmentname == "document"
    ]
    scopes = document_bodies or [(0, len(source))]

    # Work from the end so each scope retains the parser offsets established
    # for the original source.
    transformed = source
    for start, end in reversed(scopes):
        body = source[start:end]
        parsed_body = _parse(body)
        if parsed_body is None:
            continue
        regularized = _regularize_scope(body, parsed_body)
        transformed = transformed[:start] + regularized + transformed[end:]
    return transformed


def _process_file(input_path: Path, output_path: Path) -> Path:
    """Transform one UTF-8 LaTeX file and write a separate UTF-8 result.

    Parameters
    ----------
    input_path : pathlib.Path
        Source file to read without modifying.
    output_path : pathlib.Path
        Destination to create or replace with transformed source.

    Returns
    -------
    pathlib.Path
        The destination supplied by the caller.

    Raises
    ------
    OSError
        The source cannot be read or the destination cannot be written.
    """
    # Complete the transformation before opening the destination so a failure
    # cannot truncate an existing file.
    source = input_path.read_text(encoding="utf-8")
    transformed = transform_text(source)
    output_path.write_text(transformed, encoding="utf-8")
    return output_path


def main(argv: Sequence[str] | None = None) -> int:
    """Run syntax regularization in file, clipboard, or standard-stream mode.

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
        sys.stdout.write(transform_text(sys.stdin.read()))
        return 0

    if args.output_file is None and not args.no_backup:
        backup_file(args.input_file)
    output_path = args.output_file or args.input_file
    _process_file(args.input_file, output_path)
    print(f"Transformed file written to: {output_path}")
    return 0


# Parsing and source transformation


# Source layout inside these environments is intentionally opaque.
_VERBATIM_ENVIRONMENTS = frozenset(
    {"verbatim", "verbatim*", "Verbatim", "lstlisting", "minted", "comment"}
)
_TABLE_ENVIRONMENTS = frozenset(
    {"tabular", "tabular*", "array", "table", "table*", "longtable"}
)
_DISPLAY_ENVIRONMENTS = frozenset(
    {
        "displaymath", "equation", "equation*", "align", "align*", "alignat",
        "alignat*", "flalign", "flalign*", "gather", "gather*", "multline",
        "multline*", "split",
    }
)
# Standard sectioning commands introduce a new prose block in source layout.
_SECTIONING_MACROS = frozenset(
    {"part", "chapter", "section", "subsection", "subsubsection", "paragraph", "subparagraph"}
)
# Required arguments belong to environment openers rather than their contents.
_ENVIRONMENT_REQUIRED_ARGUMENTS = {
    "alignat": 1, "alignat*": 1, "array": 1, "longtable": 1, "minted": 1,
    "tabular": 1, "tabular*": 2, "thebibliography": 1,
}


def _parse(source: str) -> Any | None:
    """Parse source, returning ``None`` when it has unsafe incomplete nodes."""
    RUNTIME_DEPENDENCIES.require("pylatexenc.latexnodes.parsers")
    from pylatexenc.latexnodes.parsers import LatexGeneralNodesParser
    from pylatexenc.latexwalker import LatexWalker

    nodes, _ = LatexWalker(source).parse_content(LatexGeneralNodesParser())
    if nodes is None:
        return None

    # Unterminated tolerant-parser nodes do not have reliable source spans.
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
            if (
                getattr(children, "pos", None) is None
                or getattr(children, "pos_end", None) is None
            ):
                return None
            pending.extend(children)
        arguments = getattr(getattr(node, "nodeargd", None), "argnlist", ()) or ()
        pending.extend(argument for argument in arguments if argument is not None)
    return nodes


def _regularize_scope(source: str, nodes: Iterable[Any]) -> str:
    """Apply all layout rules to one independently parsed source scope."""
    newline = "\r\n" if "\r\n" in source else "\n"
    inline_ranges: list[tuple[int, int]] = []
    protected_ranges: list[tuple[int, int]] = []
    display_delimiters: list[tuple[int, int]] = []

    # Collect source spans once, keeping opaque environments out of recursive
    # discovery because their contents are not actionable LaTeX.
    def visit(node: Any) -> None:
        node_type = type(node).__name__
        start, end = node.pos, node.pos_end
        if node_type == "LatexEnvironmentNode":
            environment = node.environmentname
            environment_source = source[start:end]
            opening_pattern = (
                r"\\begin\s*\{" + re.escape(environment) + r"\}"
                r"(?:[ \t]*\[[^\]\r\n]*\])?"
            )
            opening_pattern += r"[ \t]*\{[^{}\r\n]*\}" * (
                _ENVIRONMENT_REQUIRED_ARGUMENTS.get(environment, 0)
            )
            opening = re.match(opening_pattern, environment_source)
            if opening:
                opening_end = start + opening.end()
                display_delimiters.append((start, opening_end))

                # A conventional label immediately after an environment
                # opener starts on the following line with no leading indent.
                label = re.match(
                    r"[ \t]*(?:\r?\n[ \t]*)?(\\label\s*\{[^{}\r\n]*\})",
                    source[opening_end:end],
                )
                if label:
                    label_start = opening_end + label.start(1)
                    display_delimiters.append(
                        (label_start, opening_end + label.end(1))
                    )
            if environment in _VERBATIM_ENVIRONMENTS:
                protected_ranges.append((start, end))
                return
            if environment in _TABLE_ENVIRONMENTS:
                protected_ranges.append((start, end))
            if environment in _DISPLAY_ENVIRONMENTS:
                protected_ranges.append((start, end))
                closing = re.search(
                    r"(\\end\s*\{" + re.escape(environment) + r"\})[ \t]*$",
                    environment_source,
                )
                if closing:
                    display_delimiters.append(
                        (start + closing.start(1), start + closing.end(1))
                    )
        elif node_type == "LatexMathNode":
            protected_ranges.append((start, end))
            if getattr(node, "displaytype", None) == "inline":
                inline_ranges.append((start, end))
            else:
                delimiters = _math_delimiters(source, start, end)
                if delimiters is not None:
                    display_delimiters.extend(delimiters)

        for child in getattr(node, "nodelist", ()) or ():
            visit(child)
        arguments = getattr(getattr(node, "nodeargd", None), "argnlist", ()) or ()
        for argument in arguments:
            if argument is not None:
                visit(argument)

    for node in nodes:
        visit(node)

    # Express display isolation and uncommented inline joins as non-overlapping
    # edits against parser positions, then apply them from right to left.
    edits: set[tuple[int, int, str]] = set()
    for start, end in display_delimiters:
        before = _break_before(source, start, newline)
        after = _break_after(source, end, newline)
        if before is not None:
            edits.add(before)
        if after is not None:
            edits.add(after)
    for start, end in inline_ranges:
        math_source = source[start:end]
        if not _contains_comment(math_source):
            for match in re.finditer(r"\r?\n[ \t]*", math_source):
                edits.add((start + match.start(), start + match.end(), ""))
    regularized = _apply_edits(source, edits)

    # Reparse after line insertion so macro offsets align with the new text,
    # then give each sectioning command a following blank physical line.
    reparsed = _parse(regularized)
    if reparsed is None:
        return regularized
    sectioning_edits = [
        edit
        for position in _sectioning_ends(reparsed, regularized)
        if (edit := _blank_line_after(regularized, position, newline)) is not None
    ]
    regularized = _apply_edits(regularized, sectioning_edits)

    # Section spacing changes offsets once more. Protect indentation only when
    # its source characters occur inside math, verbatim, or table content.
    reparsed = _parse(regularized)
    if reparsed is None:
        return regularized
    protected_ranges = _protected_ranges(reparsed)
    indentation_edits: list[tuple[int, int, str]] = []
    for match in re.finditer(r"(?m)^[ \t]+", regularized):
        first_token = match.end()
        if not any(start <= first_token < end for start, end in protected_ranges):
            indentation_edits.append((match.start(), match.end(), ""))
    return _apply_edits(regularized, indentation_edits)


def _math_delimiters(
    source: str, start: int, end: int
) -> tuple[tuple[int, int], tuple[int, int]] | None:
    """Return opening and closing spans for one parsed display math node."""
    text = source[start:end]
    for opening, closing in ((r"\[", r"\]"), ("$$", "$$")):
        if text.startswith(opening) and text.endswith(closing):
            return ((start, start + len(opening)), (end - len(closing), end))
    return None


def _contains_comment(source: str) -> bool:
    """Return whether source contains an unescaped LaTeX comment marker."""
    for index, character in enumerate(source):
        if character != "%":
            continue
        backslashes = 0
        cursor = index - 1
        while cursor >= 0 and source[cursor] == "\\":
            backslashes += 1
            cursor -= 1
        if backslashes % 2 == 0:
            return True
    return False


def _break_before(
    source: str, position: int, newline: str
) -> tuple[int, int, str] | None:
    """Return an edit that isolates a token from preceding same-line content."""
    line_start = source.rfind("\n", 0, position) + 1
    if not source[line_start:position].strip(" \t\r"):
        return None
    whitespace_start = position
    while whitespace_start > line_start and source[whitespace_start - 1] in " \t":
        whitespace_start -= 1
    return whitespace_start, position, newline


def _break_after(
    source: str, position: int, newline: str
) -> tuple[int, int, str] | None:
    """Return an edit that isolates a token from following same-line content."""
    line_end = source.find("\n", position)
    if line_end < 0:
        line_end = len(source)
    if not source[position:line_end].strip(" \t\r"):
        return None
    whitespace_end = position
    while whitespace_end < line_end and source[whitespace_end] in " \t":
        whitespace_end += 1
    return position, whitespace_end, newline


def _apply_edits(source: str, edits: Iterable[tuple[int, int, str]]) -> str:
    """Apply compatible source edits in descending positional order."""
    transformed = source
    ordered = sorted(set(edits), key=lambda edit: (edit[0], edit[1]), reverse=True)
    previous_start = len(source) + 1
    for start, end, replacement in ordered:
        if end > previous_start:
            continue
        transformed = transformed[:start] + replacement + transformed[end:]
        previous_start = start
    return transformed


def _sectioning_ends(nodes: Iterable[Any], source: str) -> tuple[int, ...]:
    """Return source ends of sectioning commands outside opaque regions."""
    positions: list[int] = []

    def visit(node: Any) -> None:
        node_type = type(node).__name__
        if node_type == "LatexMathNode":
            return
        if node_type == "LatexEnvironmentNode" and node.environmentname in (
            _DISPLAY_ENVIRONMENTS | _VERBATIM_ENVIRONMENTS | _TABLE_ENVIRONMENTS
        ):
            return
        if node_type == "LatexMacroNode" and node.macroname in _SECTIONING_MACROS:
            positions.append(_sectioning_end(source, node.pos, node.macroname))
            return
        for child in getattr(node, "nodelist", ()) or ():
            visit(child)
        arguments = getattr(getattr(node, "nodeargd", None), "argnlist", ()) or ()
        for argument in arguments:
            if argument is not None:
                visit(argument)

    for node in nodes:
        visit(node)
    return tuple(positions)


def _sectioning_end(source: str, start: int, macroname: str) -> int:
    """Return the end of a section macro's star, optional title, and title."""
    cursor = start + len(macroname) + 1

    # Resolve the conventional syntax independently of parser macro specs;
    # pylatexenc does not declare title arguments for every sectioning level.
    while cursor < len(source) and source[cursor].isspace():
        cursor += 1
    if cursor < len(source) and source[cursor] == "*":
        cursor += 1
        while cursor < len(source) and source[cursor].isspace():
            cursor += 1
    if cursor < len(source) and source[cursor] == "[":
        optional_end = _balanced_group_end(source, cursor, "[", "]")
        if optional_end is None:
            return cursor
        cursor = optional_end
        while cursor < len(source) and source[cursor].isspace():
            cursor += 1
    if cursor < len(source) and source[cursor] == "{":
        title_end = _balanced_group_end(source, cursor, "{", "}")
        if title_end is not None:
            return title_end
    return cursor


def _balanced_group_end(
    source: str, start: int, opening: str, closing: str
) -> int | None:
    """Return the position after one balanced, escape-aware source group."""
    depth = 0
    for position in range(start, len(source)):
        character = source[position]
        backslashes = 0
        cursor = position - 1
        while cursor >= start and source[cursor] == "\\":
            backslashes += 1
            cursor -= 1
        if backslashes % 2:
            continue
        if character == opening:
            depth += 1
        elif character == closing:
            depth -= 1
            if depth == 0:
                return position + 1
    return None


def _blank_line_after(
    source: str, position: int, newline: str
) -> tuple[int, int, str] | None:
    """Return the edit needed for a blank line after one sectioning macro."""
    cursor = position
    while cursor < len(source) and source[cursor] in " \t":
        cursor += 1

    # A comment on the heading line belongs to the heading. Place the blank
    # line after its terminating newline rather than detaching the comment.
    if cursor < len(source) and source[cursor] == "%":
        line_end = source.find("\n", cursor)
        if line_end < 0:
            return len(source), len(source), newline + newline
        first_break_end = line_end + 1
    elif source.startswith("\r\n", cursor):
        first_break_end = cursor + 2
    elif cursor < len(source) and source[cursor] == "\n":
        first_break_end = cursor + 1
    elif cursor == len(source):
        return position, len(source), newline + newline
    else:
        return position, cursor, newline + newline

    # Whitespace on an already blank second line counts as an existing blank
    # line and will be normalized later by the indentation rule.
    second_break = first_break_end
    while second_break < len(source) and source[second_break] in " \t":
        second_break += 1
    if source.startswith("\r\n", second_break) or (
        second_break < len(source) and source[second_break] == "\n"
    ):
        return None
    return first_break_end, first_break_end, newline


def _protected_ranges(nodes: Iterable[Any]) -> tuple[tuple[int, int], ...]:
    """Return source interiors whose indentation must remain unchanged."""
    ranges: list[tuple[int, int]] = []

    def visit(node: Any) -> None:
        node_type = type(node).__name__
        if node_type == "LatexMathNode":
            # Delimiters are boundaries rather than math contents. Protecting
            # only the parsed body removes indentation before \( and \[ while
            # retaining intentional alignment between the delimiters.
            content = getattr(node, "nodelist", None)
            if content is not None:
                ranges.append((content.pos, content.pos_end))
            return
        if (
            node_type == "LatexEnvironmentNode"
            and node.environmentname in _DISPLAY_ENVIRONMENTS
        ):
            content = getattr(node, "nodelist", None)
            if content is not None:
                ranges.append((content.pos, content.pos_end))
            return
        if node_type == "LatexEnvironmentNode" and node.environmentname in (
            _VERBATIM_ENVIRONMENTS | _TABLE_ENVIRONMENTS
        ):
            ranges.append((node.pos, node.pos_end))
            return
        for child in getattr(node, "nodelist", ()) or ():
            visit(child)
        arguments = getattr(getattr(node, "nodeargd", None), "argnlist", ()) or ()
        for argument in arguments:
            if argument is not None:
                visit(argument)

    for node in nodes:
        visit(node)
    return tuple(ranges)


# Dependency and command boundaries


# Keep only this command's dependency declarations at its external boundary.
RUNTIME_DEPENDENCIES = DependencyManager(
    {
        "pylatexenc.latexnodes.parsers": "pylatexenc>=3.0a33",
        "pyperclip": "pyperclip>=1.9",
    }
)


def _build_parser() -> argparse.ArgumentParser:
    """Build the interface for file, clipboard, and standard-stream workflows."""
    parser = argparse.ArgumentParser(description="Regularize LaTeX source layout.")
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


def _default_output_path(input_path: Path) -> Path:
    """Return a sibling path with ``_regularized`` before its extension."""
    suffix = input_path.suffix or ".tex"
    stem = input_path.stem if input_path.suffix else input_path.name
    return input_path.with_name(f"{stem}_regularized{suffix}")


def _transform_clipboard() -> None:
    """Transform nonempty clipboard text and copy it back only on success."""
    pyperclip = RUNTIME_DEPENDENCIES.require("pyperclip")
    source = pyperclip.paste()
    if not source.strip():
        print("Clipboard is empty; nothing was changed.")
        return
    pyperclip.copy(transform_text(source))
    print("Regularized LaTeX written back to the clipboard.")


if __name__ == "__main__":
    raise SystemExit(main())
