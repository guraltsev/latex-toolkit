r"""This module formats LaTeX prose with one sentence on each physical source line.

The ``transform_text(...)`` API accepts fragments or complete documents. Comments,
paragraph breaks, math, verbatim-like content, structural environments, and
text outside document environments retain their original source spelling.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from latex_toolkit.lib.dependencies import DependencyManager
from latex_toolkit.lib.backup import backup_file


@dataclass(frozen=True)
class _TextMacro:
    """Describe one text-bearing macro and its recursively nested prose."""

    start: int
    end: int
    content_start: int
    content_end: int
    kind: str
    children: tuple[_TextMacro, ...]


@dataclass(frozen=True)
class _Replacement:
    """Associate a source span with transformed opaque content."""

    start: int
    end: int
    text: str
    kind: str


# Keep parser, clipboard, and formatter installation at the command boundary
# so importing the text API does not perform external setup.
RUNTIME_DEPENDENCIES = DependencyManager(
    {
        "pylatexenc.latexnodes.parsers": "pylatexenc>=3.0a33",
        "pyperclip": "pyperclip>=1.9",
        "snapper": "snapper-fmt==0.7.9",
    }
)


# These environments own source layout or non-prose structure in the initial
# policy. Captions nested in a structural environment are still found first.
_VERBATIM_ENVIRONMENTS = frozenset(
    {"verbatim", "verbatim*", "Verbatim", "lstlisting", "minted", "comment"}
)
# These environments use display-math layout that prose formatting must retain.
_DISPLAY_ENVIRONMENTS = frozenset(
    {
        "displaymath",
        "equation",
        "equation*",
        "align",
        "align*",
        "alignat",
        "alignat*",
        "gather",
        "gather*",
        "multline",
        "multline*",
        "flalign",
        "flalign*",
        "split",
    }
)
# These environments contain structure whose line layout is user-controlled.
_STRUCTURAL_ENVIRONMENTS = frozenset(
    {
        "tabular",
        "tabular*",
        "array",
        "table",
        "table*",
        "figure",
        "figure*",
        "tikzpicture",
        "thebibliography",
    }
)


def transform_text(source: str) -> str:
    r"""Format prose sentences while preserving protected LaTeX source.

    Complete documents are formatted only inside top-level ``document``
    environments. Input without a document environment is treated as a LaTeX
    fragment. Nested captions and footnotes are formatted before their parent
    prose, and footnote invocations are isolated on source lines without
    changing TeX spacing.

    Parameters
    ----------
    source : str
        LaTeX source in a complete document or fragment form.

    Returns
    -------
    str
        Source with sentence-boundary whitespace replaced by physical newlines.

    Raises
    ------
    RuntimeError
        Snapper is unavailable, exits unsuccessfully, or violates an opaque
        source-preservation contract.

    Examples
    --------
    Basic usage:

    >>> transform_text("First sentence. Second sentence.")
    'First sentence.\nSecond sentence.'
    """
    if not source:
        return source

    nodes = _parse(source)
    if nodes is None:
        return source
    document_bodies = [
        (node.nodelist.pos, node.nodelist.pos_end, node.nodelist)
        for node in nodes
        if type(node).__name__ == "LatexEnvironmentNode"
        and node.environmentname == "document"
    ]

    # A fragment is a synthetic document body; complete-document preambles and
    # material after each document environment are never sent to the formatter.
    scopes = document_bodies or [(0, len(source), nodes)]
    transformed = source
    for start, end, scope_nodes in reversed(scopes):
        macros = _find_text_macros(scope_nodes, source)
        replacements = tuple(_render_macro(source, macro) for macro in macros)
        body = _format_scope(source[start:end], start, replacements)
        transformed = transformed[:start] + body + transformed[end:]
    return transformed


def _process_file(input_path: Path, output_path: Path) -> Path:
    """Transform one UTF-8 LaTeX file and write a separate UTF-8 result.

    The complete transformation succeeds before the destination is opened, so
    a formatter failure cannot truncate either path.

    Parameters
    ----------
    input_path : pathlib.Path
        Source file to read without modifying.
    output_path : pathlib.Path
        Destination to create or replace after a successful transformation.

    Returns
    -------
    pathlib.Path
        The destination path supplied by the caller.

    Raises
    ------
    OSError
        The source cannot be read or destination cannot be written.
    RuntimeError
        The formatter fails before any output is written.

    Examples
    --------
    Basic usage:

    >>> from pathlib import Path
    >>> from tempfile import TemporaryDirectory
    >>> with TemporaryDirectory() as directory:
    ...     source = Path(directory) / "paper.tex"
    ...     output = Path(directory) / "paper_sentences.tex"
    ...     _ = source.write_text("First. Second.", encoding="utf-8")
    ...     result = _process_file(source, output)
    ...     print(result.name, output.read_text(encoding="utf-8"))
    paper_sentences.tex First.
    Second.
    """
    with input_path.open("r", encoding="utf-8", newline="") as input_file:
        source = input_file.read()
    transformed = transform_text(source)
    with output_path.open("w", encoding="utf-8", newline="") as output_file:
        output_file.write(transformed)
    return output_path


def main(argv: Sequence[str] | None = None) -> int:
    """Run the formatter in file, clipboard, or standard-stream mode.

    With no arguments, the command transforms the system clipboard.

    Parameters
    ----------
    argv : sequence of str, optional
        Command-line arguments without the executable name.

    Returns
    -------
    int
        Zero after a completed transformation.

    Raises
    ------
    SystemExit
        Arguments select multiple input modes or combine a non-file mode with
        an output path.
    """
    parser = _build_parser()
    args = parser.parse_args(argv)

    # Default to clipboard mode when the caller does not provide an input file
    # or an explicit mode flag.
    if args.input_file is None and not args.clipboard and not args.stdin:
        args.clipboard = True

    # Reject ambiguous input modes before performing any transformation.
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


# Prose-scope discovery


def _parse(source: str) -> Any | None:
    """Parse source, returning ``None`` when pylatexenc reports incomplete input."""
    RUNTIME_DEPENDENCIES.require("pylatexenc.latexnodes.parsers")
    from pylatexenc.latexnodes.parsers import LatexGeneralNodesParser
    from pylatexenc.latexwalker import LatexWalker, get_default_latex_context_db
    from pylatexenc.macrospec import MacroSpec

    # Copy the default database before overriding macro specs; mutating the
    # process-wide default would leak parser behavior to embedding programs.
    default_context = get_default_latex_context_db()
    context = default_context.filtered_context(
        keep_categories=default_context.category_list
    )
    context.add_context_category(
        "sentence-per-line",
        macros=[MacroSpec("caption", "[{"), MacroSpec("footnote", "[{")],
        prepend=True,
    )
    walker = LatexWalker(source, latex_context=context)
    nodes, _ = walker.parse_content(LatexGeneralNodesParser())

    # Tolerant parsing represents unmatched closing constructs with no top-level
    # node list and unterminated environments with child lists lacking spans.
    # Either state is unsafe for source slicing, so leave that scope opaque.
    if nodes is None:
        return None
    pending = list(nodes)
    visited: set[int] = set()
    while pending:
        node = pending.pop()
        if id(node) in visited:
            continue
        visited.add(id(node))

        child_nodes = getattr(node, "nodelist", None)
        if child_nodes is not None:
            if (
                getattr(child_nodes, "pos", None) is None
                or getattr(child_nodes, "pos_end", None) is None
            ):
                return None
            pending.extend(child_nodes)
        parsed_arguments = getattr(node, "nodeargd", None)
        pending.extend(
            argument
            for argument in (getattr(parsed_arguments, "argnlist", ()) or ())
            if argument is not None
        )
    return nodes


def _find_text_macros(nodes: Iterable[Any], source: str) -> tuple[_TextMacro, ...]:
    """Return outermost caption and footnote scopes in a parsed node sequence."""
    found: list[_TextMacro] = []
    visited: set[int] = set()

    def visit(node: Any) -> None:
        """Collect text-bearing macro ranges from one parser node."""
        if id(node) in visited:
            return
        visited.add(id(node))

        # Verbatim content cannot contain actionable LaTeX, so even text-like
        # spellings inside it remain opaque.
        if (
            type(node).__name__ == "LatexEnvironmentNode"
            and node.environmentname in _VERBATIM_ENVIRONMENTS
        ):
            return

        if (
            type(node).__name__ == "LatexMacroNode"
            and node.macroname in {"caption", "footnote"}
        ):
            arguments = [
                argument
                for argument in (getattr(node.nodeargd, "argnlist", ()) or ())
                if argument is not None
            ]
            mandatory = next(
                (
                    argument
                    for argument in reversed(arguments)
                    if source[argument.pos : argument.pos + 1] == "{"
                ),
                None,
            )
            if mandatory is not None:
                children = _find_text_macros(mandatory.nodelist, source)
                found.append(
                    _TextMacro(
                        start=node.pos,
                        end=node.pos_end,
                        content_start=mandatory.pos + 1,
                        content_end=mandatory.pos_end - 1,
                        kind=node.macroname,
                        children=children,
                    )
                )
                return

        parsed_arguments = getattr(node, "nodeargd", None)
        for argument in getattr(parsed_arguments, "argnlist", ()) or ():
            if argument is not None:
                visit(argument)
        for child in getattr(node, "nodelist", ()) or ():
            if child is not None:
                visit(child)

    for candidate in nodes:
        visit(candidate)
    return tuple(sorted(found, key=lambda macro: macro.start))


def _render_macro(source: str, macro: _TextMacro) -> _Replacement:
    """Format a text-bearing macro argument and return its complete invocation."""
    children = tuple(_render_macro(source, child) for child in macro.children)
    content = _format_scope(
        source[macro.content_start : macro.content_end],
        macro.content_start,
        children,
    )
    invocation = (
        source[macro.start : macro.content_start]
        + content
        + source[macro.content_end : macro.end]
    )
    return _Replacement(macro.start, macro.end, invocation, macro.kind)


# Paragraph formatting and protected-source restoration


def _format_scope(
    source: str,
    source_offset: int,
    children: tuple[_Replacement, ...],
) -> str:
    """Format one prose scope while treating processed children as immutable."""
    protected: dict[str, str] = {}
    child_tokens: list[tuple[str, str]] = []
    pieces: list[str] = []
    cursor = 0

    # Replace transformed children before parsing the parent. Their unique
    # tokens survive all parent passes and prevent nested content reformatting.
    for index, child in enumerate(children):
        local_start = child.start - source_offset
        local_end = child.end - source_offset
        token = _new_token(source, protected, f"CHILD{index}")
        pieces.append(source[cursor:local_start])
        pieces.append(token)
        protected[token] = child.text
        child_tokens.append((token, child.kind))
        cursor = local_end
    pieces.append(source[cursor:])
    masked = "".join(pieces)

    # Footnotes are line blocks in their parent scope. Synthetic comments are
    # used only where a direct newline would introduce a TeX space.
    newline = "\r\n" if "\r\n" in source else "\n"
    for token, kind in child_tokens:
        if kind == "footnote":
            masked = _isolate_footnote(masked, token, newline)

    # Structural and display spans divide formatting work without becoming
    # mutable. Formatting resumes on both sides of protected display source.
    boundaries = _boundary_ranges(masked)
    inline_ranges = _inline_ranges(masked)
    output: list[str] = []
    cursor = 0
    for start, end in boundaries:
        piece_ranges = tuple(
            (range_start - cursor, range_end - cursor, kind)
            for range_start, range_end, kind in inline_ranges
            if cursor <= range_start and range_end <= start
        )
        output.append(
            _format_piece(
                masked[cursor:start], newline, piece_ranges, tuple(child_tokens)
            )
        )
        output.append(masked[start:end])
        cursor = end
    piece_ranges = tuple(
        (range_start - cursor, range_end - cursor, kind)
        for range_start, range_end, kind in inline_ranges
        if cursor <= range_start and range_end <= len(masked)
    )
    output.append(
        _format_piece(masked[cursor:], newline, piece_ranges, tuple(child_tokens))
    )
    result = "".join(output)
    return _restore_tokens(result, protected)


def _boundary_ranges(source: str) -> tuple[tuple[int, int], ...]:
    """Locate real paragraph delimiters and opaque block-level source spans."""
    ranges: list[tuple[int, int]] = []
    nodes = _parse(source)
    if nodes is None:
        return ((0, len(source)),)

    def visit(node: Any) -> None:
        """Collect protected source ranges from one parser node."""
        node_type = type(node).__name__
        if (
            node_type == "LatexMathNode"
            and getattr(node, "displaytype", None) == "display"
        ):
            ranges.append(_expand_display_whitespace(source, node.pos, node.pos_end))
            return
        if node_type == "LatexEnvironmentNode":
            name = node.environmentname
            if name in _DISPLAY_ENVIRONMENTS:
                ranges.append(
                    _expand_display_whitespace(source, node.pos, node.pos_end)
                )
                return
            if name in _STRUCTURAL_ENVIRONMENTS or name in _VERBATIM_ENVIRONMENTS:
                ranges.append((node.pos, node.pos_end))
                return
        if node_type == "LatexMacroNode" and node.macroname == "par":
            ranges.append((node.pos, node.pos_end))
            return
        for child in getattr(node, "nodelist", ()) or ():
            visit(child)
        parsed_arguments = getattr(node, "nodeargd", None)
        for argument in getattr(parsed_arguments, "argnlist", ()) or ():
            if argument is not None:
                visit(argument)

    for node in nodes:
        visit(node)

    # Blank lines are application-level paragraph tokens. They remain exact
    # source even when the parser represents their characters in larger nodes.
    ranges.extend(
        match.span()
        for match in re.finditer(r"(?:\r?\n)[ \t]*(?:\r?\n)+", source)
    )
    return _merge_ranges(ranges)


def _inline_ranges(source: str) -> tuple[tuple[int, int, str], ...]:
    """Locate comments, inline math, and verb macros in one complete scope."""
    ranges: list[tuple[int, int, str]] = []
    nodes = _parse(source)
    if nodes is None:
        return ((0, len(source), "opaque"),)

    def visit(node: Any) -> None:
        """Collect inline ranges from one parser node."""
        node_type = type(node).__name__
        if node_type == "LatexCommentNode":
            ranges.append((node.pos, node.pos_end, "opaque"))
            return
        if node_type == "LatexMathNode":
            ranges.append((node.pos, node.pos_end, "math"))
            return
        if node_type == "LatexMacroNode" and node.macroname in {"verb", "Verb"}:
            ranges.append((node.pos, node.pos_end, "opaque"))
            return
        for child in getattr(node, "nodelist", ()) or ():
            visit(child)
        parsed_arguments = getattr(node, "nodeargd", None)
        for argument in getattr(parsed_arguments, "argnlist", ()) or ():
            if argument is not None:
                visit(argument)

    for node in nodes:
        visit(node)
    return tuple(sorted(ranges))


def _format_piece(
    source: str,
    newline: str,
    protected_ranges: tuple[tuple[int, int, str], ...],
    child_tokens: tuple[tuple[str, str], ...],
) -> str:
    """Send one non-block prose slice through Snapper with immutable tokens."""
    if not source or not source.strip():
        return source

    # Ordinary single newlines are source wrapping for Snapper to collapse.
    # Keep edge layout and boundaries beside processed child macro scopes,
    # whose punctuation is hidden inside opaque placeholders during this pass.
    ranges = [(start, end) for start, end, _ in protected_ranges]
    fixed_line_tokens = tuple(token for token, _ in child_tokens)
    for match in re.finditer(r"\r?\n[ \t]*", source):
        at_source_edge = match.start() == 0 or match.end() == len(source)
        beside_fixed_line_token = any(
            source.startswith(token, match.end())
            or source[: match.start()].endswith(token)
            for token in fixed_line_tokens
        )
        if at_source_edge or beside_fixed_line_token:
            ranges.append(match.span())
    leading = re.match(r"[ \t]+", source)
    trailing = re.search(r"[ \t]+$", source)
    if leading:
        ranges.append(leading.span())
    if trailing:
        ranges.append(trailing.span())

    # Piece-local mappings exclude child tokens, which are deliberately left
    # opaque until the complete parent scope has been reassembled.
    piece_protected: dict[str, str] = {}
    masked = _replace_ranges(source, _merge_ranges(ranges), piece_protected)
    formatted = _run_snapper(masked)
    formatted = formatted.replace("\r\n", "\n").replace("\n", newline)
    return _restore_tokens(formatted, piece_protected)


def _replace_ranges(
    source: str,
    ranges: tuple[tuple[int, int], ...],
    protected: dict[str, str],
) -> str:
    """Replace immutable source ranges with sentence-safe opaque words."""
    output: list[str] = []
    cursor = 0
    for index, (start, end) in enumerate(ranges):
        token = _new_token(source, protected, f"OPAQUE{index}")
        # A bare alphanumeric word prevents Snapper from treating immutable
        # whitespace itself as a replaceable sentence boundary. Existing
        # whitespace immediately outside the range remains in the source.
        placeholder = token
        output.append(source[cursor:start])
        output.append(placeholder)
        protected[placeholder] = source[start:end]
        cursor = end
    output.append(source[cursor:])
    return "".join(output)


def _restore_tokens(
    source: str,
    protected: dict[str, str],
) -> str:
    """Restore each opaque token exactly once and reject formatter corruption."""
    result = source
    pending = list(protected.items())
    while pending:
        progress = False
        for token, original in pending[:]:
            count = result.count(token)
            if count == 1:
                result = result.replace(token, original)
                pending.remove((token, original))
                progress = True
            elif count > 1:
                raise RuntimeError("snapper duplicated protected LaTeX source")
        if not progress:
            # Tokens nested inside another protected value become visible only
            # after the outer token is restored; no progress means corruption.
            raise RuntimeError("snapper deleted or rewrote protected LaTeX source")
    protected.clear()
    return result


def _new_token(source: str, protected: dict[str, str], label: str) -> str:
    """Create a stable alphanumeric placeholder absent from source and mappings."""
    serial = len(protected)
    while True:
        token = f"SPLT{label}{serial}TOKEN"
        if token not in source and all(token not in value for value in protected.values()):
            return token
        serial += 1


def _isolate_footnote(source: str, token: str, newline: str) -> str:
    """Place one footnote token on a source line without changing TeX spacing."""
    position = source.index(token)

    # Replace existing horizontal separation directly. An attached footnote
    # instead needs a comment-terminated newline to suppress a new TeX space.
    line_start = max(source.rfind("\n", 0, position), source.rfind("\r", 0, position)) + 1
    left_text = source[line_start:position]
    if left_text.strip():
        whitespace = re.search(r"[ \t]+$", source[:position])
        if whitespace:
            source = source[: whitespace.start()] + newline + source[position:]
            position = whitespace.start() + len(newline)
        else:
            source = source[:position] + "%" + newline + source[position:]
            position += len("%" + newline)

    token_end = position + len(token)
    if re.match(r"%\r?\n", source[token_end:]):
        return source
    line_end_match = re.match(r"[ \t]*(?:\r?\n|$)", source[token_end:])
    if line_end_match and line_end_match.group(0):
        return source
    whitespace = re.match(r"[ \t]+", source[token_end:])
    if whitespace:
        end = token_end + whitespace.end()
        return source[:token_end] + newline + source[end:]
    if token_end < len(source):
        return source[:token_end] + "%" + newline + source[token_end:]
    return source


def _expand_display_whitespace(source: str, start: int, end: int) -> tuple[int, int]:
    """Include contiguous non-blank layout whitespace around display math."""
    left = start
    while left > 0 and source[left - 1] in " \t":
        left -= 1
    if left > 0 and source[left - 1] == "\n":
        candidate = left - 1
        previous = source.rfind("\n", 0, candidate)
        if source[previous + 1 : candidate].strip():
            candidate = left
        left = candidate

    right = end
    while right < len(source) and source[right] in " \t":
        right += 1
    if source.startswith("\r\n", right):
        right += 2
        while right < len(source) and source[right] in " \t":
            right += 1
    elif right < len(source) and source[right] == "\n":
        right += 1
        while right < len(source) and source[right] in " \t":
            right += 1
    return left, right


def _merge_ranges(ranges: Iterable[tuple[int, int]]) -> tuple[tuple[int, int], ...]:
    """Return sorted source ranges with overlaps and adjacency coalesced."""
    merged: list[list[int]] = []
    for start, end in sorted(ranges):
        if start == end:
            continue
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return tuple((start, end) for start, end in merged)


# External process and command boundaries


def _run_snapper(source: str) -> str:
    """Format a protected LaTeX fragment with the pinned Snapper executable."""
    executable = _find_snapper()
    wrapper_newline = "\r\n" if "\r\n" in source else "\n"
    prefix = f"\\begin{{document}}{wrapper_newline}"
    suffix = f"{wrapper_newline}\\end{{document}}"
    completed = subprocess.run(
        [str(executable), "--format", "latex", "--max-width", "0"],
        input=(prefix + source + suffix).encode("utf-8"),
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        message = completed.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"snapper failed with exit code {completed.returncode}: {message}")

    output = completed.stdout.decode("utf-8")
    if not output.startswith(prefix) or not output.endswith(suffix):
        raise RuntimeError("snapper rewrote the temporary document wrapper")
    return output[len(prefix) : -len(suffix)]


def _find_snapper() -> Path:
    """Locate the executable installed by the pinned snapper-fmt distribution."""
    return RUNTIME_DEPENDENCIES.require_executable("snapper")


def _build_parser() -> argparse.ArgumentParser:
    """Build the interface for file, clipboard, and standard-stream workflows."""
    parser = argparse.ArgumentParser(
        description="Put each LaTeX prose sentence on its own source line."
    )
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
    """Return a sibling output path with ``_sentences`` before its extension."""
    suffix = input_path.suffix or ".tex"
    stem = input_path.stem if input_path.suffix else input_path.name
    return input_path.with_name(f"{stem}_sentences{suffix}")


def _transform_clipboard() -> None:
    """Transform nonempty clipboard text and copy it back only on success."""
    pyperclip = RUNTIME_DEPENDENCIES.require("pyperclip")

    source = pyperclip.paste()
    if not source.strip():
        print("Clipboard is empty; nothing was changed.")
        return
    transformed = transform_text(source)
    pyperclip.copy(transformed)
    print("Formatted LaTeX written back to the clipboard.")


if __name__ == "__main__":
    raise SystemExit(main())
