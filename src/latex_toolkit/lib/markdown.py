"""Provide preservation-focused MyST Markdown source transformations.

The public functions classify a deliberately small MyST/CommonMark dialect and
transform only ordinary paragraphs, atx headings, or TeX math spans.  Fenced
and indented code, front matter, HTML, links, tables, lists, block quotes, and
other syntax-sensitive source remain byte-identical.

Usage and API
-------------
Markdown command packages call ``regularize_text(...)``, ``sentence_text(...)``,
and the math-span transforms.  ``run_command(...)`` supplies their common file,
clipboard, and standard-stream interface.

Implementation Approach
-----------------------
Each transformation first loads and parses the document with MyST's
``markdown-it-py`` configuration.  A conservative source classifier then
identifies only source ranges whose spelling can be safely preserved while
nearby prose is rendered with deterministic whitespace.  Unrecognised and
malformed constructs are treated as opaque rather than partially rewritten.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Callable, Iterator, Sequence
from pathlib import Path

from latex_toolkit.lib.backup import backup_file
from latex_toolkit.lib.streams import configure_utf8_standard_streams


def regularize_text(source: str) -> str:
    """Render supported Markdown prose with canonical whitespace.

    Parameters
    ----------
    source : str
        MyST Markdown source.

    Returns
    -------
    str
        Source with soft wrapping collapsed in ordinary paragraphs and atx
        headings while protected Markdown syntax is unchanged.
    """
    return _transform_prose(source, sentence_lines=False)


def sentence_text(source: str) -> str:
    """Put conservative ASCII-terminal Markdown prose sentences on source lines.

    Parameters
    ----------
    source : str
        MyST Markdown source.

    Returns
    -------
    str
        Source with one supported prose sentence per physical line.

    Notes
    -----
    Abbreviations, initials, decimals, and non-ASCII terminal punctuation are
    intentionally not inferred.
    """
    return _transform_prose(source, sentence_lines=True)


def latex_to_dollar_text(source: str) -> str:
    """Convert command-style TeX math delimiters in safe Markdown prose.

    Inline ``\\(...\\)`` spans become ``$...$``.  Display delimiters are
    converted only when both delimiters occupy otherwise blank source lines,
    so the resulting ``$$`` block cannot change paragraph parsing.
    """
    _parse_myst(source)
    newline = _newline(source)
    output: list[str] = []
    for protected, segment in _segments(source):
        if protected:
            output.append(segment)
            continue
        converted = _replace_outside_inline(
            segment,
            lambda text: re.sub(
                r"\\\((.*?)\\\)", lambda match: "$" + match.group(1) + "$", text, flags=re.DOTALL
            ),
        )
        lines = converted.splitlines(keepends=True)
        for index, line in enumerate(lines):
            content = line.rstrip("\r\n")
            if re.fullmatch(r"[ \t]*\\\[[ \t]*", content):
                lines[index] = re.sub(r"\\\[", "$$", content) + (line[len(content):] or newline)
            elif re.fullmatch(r"[ \t]*\\\][ \t]*", content):
                lines[index] = re.sub(r"\\\]", "$$", content) + (line[len(content):] or newline)
        output.append("".join(lines))
    return "".join(output)


def dollar_to_latex_text(source: str) -> str:
    """Convert recognized Markdown dollar math delimiters to TeX commands.

    This interoperability transform changes only explicit dollar-delimited
    spans outside protected Markdown source.  Bare currency and unmatched
    dollar signs remain unchanged.
    """
    _parse_myst(source)
    output: list[str] = []
    for protected, segment in _segments(source):
        if protected:
            output.append(segment)
            continue
        display_open = True
        lines = segment.splitlines(keepends=True)
        for index, line in enumerate(lines):
            content = line.rstrip("\r\n")
            if re.fullmatch(r"[ \t]*\$\$[ \t]*", content):
                delimiter = r"\[" if display_open else r"\]"
                display_open = not display_open
                lines[index] = content.replace("$$", delimiter) + line[len(content):]
        segment = "".join(lines)
        output.append(_replace_outside_inline(
            segment,
            lambda text: re.sub(r"(?<!\\)\$(?!\$)([^$\r\n]+?)(?<!\\)\$", r"\\(\1\\)", text),
        ))
    return "".join(output)


def brace_math_text(source: str) -> str:
    """Apply the LaTeX bracing transform only inside Markdown TeX math spans."""
    return _transform_math(source, "brace")


def greek_unicode_to_latex_text(source: str) -> str:
    """Convert recognized Unicode symbols only inside Markdown math spans."""
    return _transform_math(source, "greek_to_latex")


def greek_latex_to_unicode_text(source: str) -> str:
    """Convert recognized LaTeX math macros only inside Markdown math spans."""
    return _transform_math(source, "greek_to_unicode")


def full_normalize_text(source: str) -> str:
    """Apply the supported canonical Markdown normalization pipeline."""
    return sentence_text(brace_math_text(latex_to_dollar_text(regularize_text(source))))


def run_command(
    argv: Sequence[str] | None,
    *,
    transform: Callable[[str], str],
    description: str,
) -> int:
    """Run one Markdown transform in file, clipboard, or stream mode."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("input_file", nargs="?", type=Path, help="UTF-8 MyST Markdown file")
    parser.add_argument("-o", "--output", "--output-file", dest="output_file", type=Path)
    parser.add_argument("-B", "--no-backup", action="store_true")
    parser.add_argument("--clipboard", action="store_true")
    parser.add_argument("--stdin", action="store_true")
    args = parser.parse_args(argv)
    if args.input_file is None and not args.clipboard and not args.stdin:
        args.clipboard = True
    if sum((args.input_file is not None, args.clipboard, args.stdin)) != 1:
        parser.error("provide an input file, --clipboard, or --stdin")
    if (args.clipboard or args.stdin) and args.output_file is not None:
        parser.error("--output cannot be used with --clipboard or --stdin")
    if args.stdin:
        configure_utf8_standard_streams()
        sys.stdout.write(transform(sys.stdin.read()))
        return 0
    if args.clipboard:
        import pyperclip
        source = pyperclip.paste()
        if not source.strip():
            print("Clipboard is empty; nothing was changed.")
            return 0
        pyperclip.copy(transform(source))
        print("Transformed Markdown written back to the clipboard.")
        return 0
    if args.output_file is None and not args.no_backup:
        backup_file(args.input_file)
    destination = args.output_file or args.input_file
    source = args.input_file.read_text(encoding="utf-8")
    destination.write_text(transform(source), encoding="utf-8")
    print(f"Transformed file written to: {destination}")
    return 0


def _transform_prose(source: str, *, sentence_lines: bool) -> str:
    """Render only accepted paragraph and atx-heading source segments."""
    _parse_myst(source)
    newline = _newline(source)
    lines = source.splitlines(keepends=True)
    output: list[str] = []
    index = 0
    while index < len(lines):
        if _is_opaque_line(lines, index):
            end = _opaque_block_end(lines, index)
            output.extend(lines[index:end])
            index = end
            continue
        if not lines[index].strip():
            output.append(lines[index])
            index += 1
            continue
        heading = re.match(r"^( {0,3}#{1,6}[ \t]+)(.*?)([ \t]*#*[ \t]*)(\r?\n)?$", lines[index])
        if heading:
            prefix, content, suffix, ending = heading.groups()
            output.append(prefix + _render_inline(content, newline, sentence_lines=False) + suffix.rstrip() + (ending or ""))
            index += 1
            continue
        end = index
        while end < len(lines) and lines[end].strip() and not _is_opaque_line(lines, end):
            if re.match(r"^ {0,3}#{1,6}[ \t]+", lines[end]):
                break
            end += 1
        paragraph = "".join(lines[index:end])
        if _has_hard_break(paragraph) or _looks_sensitive(paragraph):
            output.append(paragraph)
        else:
            output.append(_render_inline(paragraph, newline, sentence_lines=sentence_lines))
            if lines[end - 1].endswith(("\n", "\r")):
                output.append(newline)
        index = end
    return "".join(output)


def _render_inline(source: str, newline: str, *, sentence_lines: bool) -> str:
    """Canonicalize prose whitespace while hiding syntax-sensitive inline spans."""
    protected: dict[str, str] = {}
    def mask(match: re.Match[str]) -> str:
        token = f"MDTOPAQUE{len(protected)}X"
        protected[token] = match.group(0)
        return token
    # Preserve code, HTML, autolinks, and complete inline links/images exactly.
    masked = re.sub(r"(?s)(`+)(.*?)\1|<!--[\s\S]*?-->|<[^>]*>|!?\[[^\]]*\]\([^\)]*\)", mask, source)
    masked = re.sub(r"(?s)\\\(.*?\\\)|\\\[.*?\\\]|(?<!\\)\$\$.*?\$\$|(?<!\\)\$[^$\r\n]+?\$", mask, masked)
    normalized = re.sub(r"[ \t]*\r?\n[ \t]*", " ", masked)
    normalized = re.sub(r"[ \t]+", " ", normalized).strip()
    if sentence_lines:
        normalized = re.sub(r"([.!?][\"'\)\]\}]*)(?:\s+)", r"\1" + newline, normalized)
    for token, value in protected.items():
        normalized = normalized.replace(token, value)
    return normalized


def _transform_math(source: str, action: str) -> str:
    """Apply one existing LaTeX operation to source-confirmed math spans."""
    _parse_myst(source)
    if action == "brace":
        from latex_toolkit.brace_args import transform_text as transform
        def apply(span: str) -> str:
            return transform(span)
    elif action == "greek_to_latex":
        from latex_toolkit.greek_unicode2latex import transform_text as transform
        def apply(span: str) -> str:
            return transform(span)
    else:
        from latex_toolkit.greek_latex2unicode import transform_text as transform
        def apply(span: str) -> str:
            return transform(span)
    output: list[str] = []
    for protected, segment in _segments(source):
        if protected:
            output.append(segment)
            continue
        output.append(_replace_outside_inline(segment, lambda text: _replace_math_spans(text, apply)))
    return "".join(output)


def _replace_math_spans(source: str, apply: Callable[[str], str]) -> str:
    """Replace explicit TeX math spans while retaining every nonmath character."""
    pattern = re.compile(r"(?s)\\\(.*?\\\)|\\\[.*?\\\]|(?<!\\)\$\$.*?\$\$|(?<!\\)\$[^$\r\n]+?\$")
    return pattern.sub(lambda match: apply(match.group(0)), source)


def _replace_outside_inline(source: str, transform: Callable[[str], str]) -> str:
    """Apply a source transform without exposing inline Markdown syntax."""
    protected: dict[str, str] = {}

    def mask(match: re.Match[str]) -> str:
        token = f"MDTINLINE{len(protected)}X"
        protected[token] = match.group(0)
        return token

    masked = re.sub(
        r"(?s)(`+)(.*?)\1|<!--[\s\S]*?-->|<[^>]*>|!?\[[^\]]*\]\([^\)]*\)",
        mask,
        source,
    )
    result = transform(masked)
    for token, value in protected.items():
        result = result.replace(token, value)
    return result


def _parse_myst(source: str) -> None:
    """Validate source through the configured MyST parser before editing it."""
    # Configure only the extensions this command family declares: TeX math
    # plus GFM strikethrough and task lists.  The source renderer keeps tables
    # opaque, so their syntax is never reconstructed from parser tokens.
    from markdown_it.renderer import RendererHTML
    from myst_parser.config.main import MdParserConfig
    from myst_parser.parsers.mdit import create_md_parser
    parser = create_md_parser(
        MdParserConfig(enable_extensions={"dollarmath", "strikethrough", "tasklist"}),
        RendererHTML,
    )
    parser.parse(source)


def _segments(source: str) -> Iterator[tuple[bool, str]]:
    """Yield opaque blocks and editable text ranges without splitting source."""
    lines = source.splitlines(keepends=True)
    index = 0
    editable: list[str] = []
    while index < len(lines):
        if _is_opaque_line(lines, index):
            if editable:
                yield False, "".join(editable)
                editable = []
            end = _opaque_block_end(lines, index)
            yield True, "".join(lines[index:end])
            index = end
        else:
            editable.append(lines[index])
            index += 1
    if editable:
        yield False, "".join(editable)


def _is_opaque_line(lines: list[str], index: int) -> bool:
    """Return whether a line begins a preserved Markdown construct."""
    line = lines[index].rstrip("\r\n")
    if index == 0 and re.fullmatch(r"---|\+\+\+", line):
        return True
    if re.match(r"^ {0,3}(`{3,}|~{3,})", line):
        return True
    if re.match(r"^ {0,3}:{3,}", line):
        return True
    if re.match(r"^(?: {4}|\t)", line):
        return True
    if re.match(r"^ {0,3}(?:[-+*] |\d+[.)] |> ?)", line):
        return True
    if re.match(r"^ {0,3}\[[^\]]+\]:", line):
        return True
    if re.fullmatch(r" {0,3}(?:\* *\* *\*|- *- *-|_ *_ *_)[ \t]*", line):
        return True
    if re.match(r"^ {0,3}</?(?:address|article|aside|base|blockquote|body|div|dl|fieldset|figure|footer|form|h[1-6]|header|hr|ol|p|pre|script|section|style|table|ul)\b", line, re.I):
        return True
    if "|" in line and index + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-{3,}", lines[index + 1]):
        return True
    if index + 1 < len(lines) and re.fullmatch(r"[=-]+[ \t]*", lines[index + 1].rstrip("\r\n")):
        return True
    return False


def _opaque_block_end(lines: list[str], start: int) -> int:
    """Return the exclusive end of one preserved source block."""
    line = lines[start].rstrip("\r\n")
    if start == 0 and re.fullmatch(r"---|\+\+\+", line):
        delimiter = line
        for index in range(start + 1, len(lines)):
            if lines[index].rstrip("\r\n") == delimiter:
                return index + 1
        return len(lines)
    fence = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
    if fence:
        marker = fence.group(1)
        closing = re.compile(r"^ {0,3}" + re.escape(marker[0]) + "{" + str(len(marker)) + r",}[ \t]*$")
        for index in range(start + 1, len(lines)):
            if closing.match(lines[index].rstrip("\r\n")):
                return index + 1
        return len(lines)
    if re.match(r"^ {0,3}:{3,}", line):
        for index in range(start + 1, len(lines)):
            if re.match(r"^ {0,3}:{3,}[ \t]*$", lines[index].rstrip("\r\n")):
                return index + 1
        return len(lines)
    if re.match(r"^(?: {4}|\t)", line):
        index = start + 1
        while index < len(lines) and (not lines[index].strip() or re.match(r"^(?: {4}|\t)", lines[index])):
            index += 1
        return index
    if re.match(r"^ {0,3}(?:[-+*] |\d+[.)] |> ?)", line):
        index = start + 1
        while index < len(lines) and lines[index].strip():
            index += 1
        return index
    if "|" in line and start + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-{3,}", lines[start + 1]):
        index = start + 2
        while index < len(lines) and "|" in lines[index] and lines[index].strip():
            index += 1
        return index
    return start + 1


def _has_hard_break(source: str) -> bool:
    """Return whether joining a line would alter a Markdown hard break."""
    return bool(re.search(r"(?: {2,}|\\)\r?\n", source))


def _looks_sensitive(source: str) -> bool:
    """Return whether an unclassified paragraph has syntax worth preserving."""
    return bool(re.search(r"(?m)^\s*(?:::{3,}|\{[^}]+\})", source))


def _newline(source: str) -> str:
    """Return the established source newline convention."""
    return "\r\n" if "\r\n" in source else "\n"
