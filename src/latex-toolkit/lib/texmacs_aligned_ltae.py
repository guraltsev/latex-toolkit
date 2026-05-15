"""Rewrite strict TeXmacs ``aligned`` tables as ``ltae`` tables.

The conversion targets TeXmacs markup of the form
``<aligned|t|<tformat|<table|...>>>`` only when every row has exactly two
cells and the first cell is empty. Other TeXmacs constructs, including
non-strict ``aligned`` tables, are preserved while nested strict tables are
still converted.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .core import TexFile, read_tex_file


@dataclass(frozen=True, slots=True)
class _Span:
    """A half-open source span inside TeXmacs markup."""

    start: int
    end: int


@dataclass(frozen=True, slots=True)
class _Node:
    """A parsed TeXmacs angle construct with top-level argument spans."""

    start: int
    content_start: int
    content_end: int
    end: int
    parts: tuple[_Span, ...]


def convert_tex_file(source: str | Path | TexFile) -> TexFile:
    """Convert ``source`` and return an anonymous :class:`TexFile`.

    Parameters
    ----------
    source : str or pathlib.Path or TexFile
        Source file path or already loaded TeXmacs buffer.

    Returns
    -------
    TexFile
        Anonymous buffer with strict ``aligned`` tables rewritten as ``ltae``.
    """

    tex_file = _coerce_to_tex_file(source)
    return TexFile.anonymous(convert_text(tex_file.code))


def alignedt_to_ltae(source: str | Path | TexFile) -> TexFile:
    """Rewrite strict TeXmacs ``aligned`` tables as ``ltae`` tables.

    Parameters
    ----------
    source : str or pathlib.Path or TexFile
        Source file path or already loaded TeXmacs buffer.

    Returns
    -------
    TexFile
        Anonymous buffer with converted ``ltae`` tables.
    """

    return convert_tex_file(source)


def convert_text(text: str) -> str:
    """Convert raw TeXmacs markup from strict ``aligned`` tables to ``ltae``.

    Parameters
    ----------
    text : str
        TeXmacs source text to transform.

    Returns
    -------
    str
        Source text with strict ``<aligned|t|...>`` tables rewritten. Malformed
        snippets and non-strict tables are preserved.
    """

    return _rewrite_text(text)


def _coerce_to_tex_file(source: str | Path | TexFile) -> TexFile:
    if isinstance(source, TexFile):
        return source
    return read_tex_file(source)


def _rewrite_text(text: str) -> str:
    rendered: list[str] = []
    cursor = 0

    # Walk complete angle constructs so nested tables are transformed before
    # their containing source is emitted.
    while cursor < len(text):
        start = _next_unescaped(text, "<", cursor)
        if start is None:
            rendered.append(text[cursor:])
            break

        node = _parse_node_at(text, start)
        if node is None:
            rendered.append(text[cursor : start + 1])
            cursor = start + 1
            continue

        rendered.append(text[cursor:start])
        converted = _convert_aligned_node(text, node)
        if converted is None:
            rendered.append("<")
            rendered.append(_rewrite_text(text[node.content_start : node.content_end]))
            rendered.append(">")
        else:
            rendered.append(converted)
        cursor = node.end

    return "".join(rendered)


def _convert_aligned_node(text: str, node: _Node) -> str | None:
    parts = node.parts
    if len(parts) != 3:
        return None
    if _part_text(text, parts[0]) != "aligned":
        return None
    if _part_text(text, parts[1]).strip() != "t":
        return None

    converted_tformat = _convert_tformat(_part_text(text, parts[2]))
    if converted_tformat is None:
        return None
    return f"<ltae|{converted_tformat}>"


def _convert_tformat(text: str) -> str | None:
    single = _single_node(text)
    if single is None:
        return None

    prefix, node, suffix = single
    parts = node.parts
    if len(parts) != 2 or _part_text(text, parts[0]) != "tformat":
        return None

    converted_table = _convert_table(_part_text(text, parts[1]))
    if converted_table is None:
        return None
    return f"{prefix}<tformat|{converted_table}>{suffix}"


def _convert_table(text: str) -> str | None:
    single = _single_node(text)
    if single is None:
        return None

    prefix, node, suffix = single
    parts = node.parts
    if len(parts) < 2 or _part_text(text, parts[0]) != "table":
        return None

    converted_rows: list[str] = []
    for row_part in parts[1:]:
        converted_row = _convert_row(_part_text(text, row_part))
        if converted_row is None:
            return None
        converted_rows.append(converted_row)

    return f"{prefix}<table|{'|'.join(converted_rows)}>{suffix}"


def _convert_row(text: str) -> str | None:
    single = _single_node(text)
    if single is None:
        return None

    prefix, node, suffix = single
    parts = node.parts
    if len(parts) != 3 or _part_text(text, parts[0]) != "row":
        return None
    if not _is_empty_cell(_part_text(text, parts[1])):
        return None

    converted_cell = _convert_payload_cell(_part_text(text, parts[2]))
    if converted_cell is None:
        return None
    return f"{prefix}<row|{converted_cell}>{suffix}"


def _is_empty_cell(text: str) -> bool:
    single = _single_node(text)
    if single is None:
        return False

    _, node, _ = single
    parts = node.parts
    return (
        len(parts) == 2
        and _part_text(text, parts[0]) == "cell"
        and _part_text(text, parts[1]).strip() == ""
    )


def _convert_payload_cell(text: str) -> str | None:
    single = _single_node(text)
    if single is None:
        return None

    prefix, node, suffix = single
    parts = node.parts
    if len(parts) != 2 or _part_text(text, parts[0]) != "cell":
        return None

    payload = _rewrite_text(_part_text(text, parts[1]))
    return f"{prefix}<cell|{payload}>{suffix}"


def _single_node(text: str) -> tuple[str, _Node, str] | None:
    start = _skip_whitespace(text, 0)
    if start >= len(text) or text[start] != "<" or _is_escaped(text, start):
        return None

    node = _parse_node_at(text, start)
    if node is None:
        return None

    suffix_start = _skip_whitespace(text, node.end)
    if suffix_start != len(text):
        return None
    return text[:start], node, text[node.end :]


def _parse_node_at(text: str, start: int) -> _Node | None:
    if text[start] != "<" or _is_escaped(text, start):
        return None

    end = _matching_angle_end(text, start)
    if end is None:
        return None

    content_start = start + 1
    content_end = end - 1
    parts = _split_top_level_parts(text, content_start, content_end)
    return _Node(
        start=start,
        content_start=content_start,
        content_end=content_end,
        end=end,
        parts=parts,
    )


def _matching_angle_end(text: str, start: int) -> int | None:
    depth = 1
    index = start + 1
    while index < len(text):
        char = text[index]
        if char == "<" and not _is_escaped(text, index):
            depth += 1
        elif char == ">" and not _is_escaped(text, index):
            depth -= 1
            if depth == 0:
                return index + 1
        index += 1
    return None


def _split_top_level_parts(text: str, start: int, end: int) -> tuple[_Span, ...]:
    parts: list[_Span] = []
    depth = 0
    part_start = start
    index = start
    while index < end:
        char = text[index]
        if char == "<" and not _is_escaped(text, index):
            depth += 1
        elif char == ">" and not _is_escaped(text, index) and depth > 0:
            depth -= 1
        elif char == "|" and not _is_escaped(text, index) and depth == 0:
            parts.append(_Span(part_start, index))
            part_start = index + 1
        index += 1

    parts.append(_Span(part_start, end))
    return tuple(parts)


def _part_text(text: str, span: _Span) -> str:
    return text[span.start : span.end]


def _next_unescaped(text: str, needle: str, start: int) -> int | None:
    index = start
    while True:
        index = text.find(needle, index)
        if index == -1:
            return None
        if not _is_escaped(text, index):
            return index
        index += 1


def _is_escaped(text: str, index: int) -> bool:
    slash_count = 0
    probe = index - 1
    while probe >= 0 and text[probe] == "\\":
        slash_count += 1
        probe -= 1
    return slash_count % 2 == 1


def _skip_whitespace(text: str, start: int) -> int:
    index = start
    while index < len(text) and text[index].isspace():
        index += 1
    return index
