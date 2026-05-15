r"""Helpers for converting ``ltae`` environments into top-aligned blocks.

Balanced ``\begin{ltae}`` / ``\end{ltae}`` environments are rewritten as
``\begin{aligned}[t]`` / ``\end{aligned}`` blocks. The body rewrite adds a
leading ``&`` to each top-level row while preserving nested environments such
as ``cases``.
"""

from __future__ import annotations

from pathlib import Path

from latex_toolkit.lib.core import TexFile, read_tex_file
from latex_toolkit.lib.latex_parser import (
    LatexToken,
    extract_environment_name,
    find_matching_environment_block,
    split_document_regions,
    tokenize_latex,
)


def convert_tex_file(source: str | Path | TexFile) -> TexFile:
    """Convert ``source`` and return an anonymous :class:`TexFile`.

    Parameters
    ----------
    source : str or pathlib.Path or TexFile
        Source file path or already loaded TeX buffer.

    Returns
    -------
    TexFile
        Anonymous buffer with ``ltae`` environments rewritten.
    """

    tex_file = _coerce_to_tex_file(source)
    return TexFile.anonymous(convert_text(tex_file.code))


def ltae_to_aligned(source: str | Path | TexFile) -> TexFile:
    """Rewrite ``ltae`` environments as ``aligned[t]`` environments.

    Parameters
    ----------
    source : str or pathlib.Path or TexFile
        Source file path or already loaded TeX buffer.

    Returns
    -------
    TexFile
        Anonymous buffer with converted environments.
    """

    return convert_tex_file(source)


def convert_text(text: str) -> str:
    """Convert raw LaTeX text from ``ltae`` to ``aligned[t]`` blocks.

    Parameters
    ----------
    text : str
        LaTeX source text to transform.

    Returns
    -------
    str
        Source text with document-body ``ltae`` environments rewritten when a
        balanced ``document`` environment exists, otherwise with all balanced
        ``ltae`` environments rewritten.
    """

    preamble, begin_doc, body, end_doc, postamble = split_document_regions(text)
    active_text = body if begin_doc and end_doc else text
    converted = _rewrite_ltae(active_text)
    if begin_doc and end_doc:
        return f"{preamble}{begin_doc}{converted}{end_doc}{postamble}"
    return converted


def _coerce_to_tex_file(source: str | Path | TexFile) -> TexFile:
    if isinstance(source, TexFile):
        return source
    return read_tex_file(source)


def _rewrite_ltae(text: str) -> str:
    tokens = tokenize_latex(text)
    rendered: list[str] = []
    cursor = 0

    for token_index, token in enumerate(tokens):
        if token.start < cursor:
            continue
        if token.kind != "BEGIN_ENV" or extract_environment_name(token) != "ltae":
            continue

        block = find_matching_environment_block(tokens, token_index)
        if block is None:
            continue

        body = _rewrite_ltae(text[block.body_start : block.body_end])
        rendered.append(text[cursor : token.start])
        rendered.append(rf"\begin{{aligned}}[t]{_prefix_top_level_rows(body)}\end{{aligned}}")
        cursor = tokens[block.close_token_index].end

    rendered.append(text[cursor:])
    return "".join(rendered)


def _prefix_top_level_rows(body: str) -> str:
    insertion_points = _top_level_row_prefix_points(body)
    if not insertion_points:
        return body

    rendered: list[str] = []
    cursor = 0
    for point in insertion_points:
        rendered.append(body[cursor:point])
        rendered.append("&")
        cursor = point
    rendered.append(body[cursor:])
    return "".join(rendered)


def _top_level_row_prefix_points(body: str) -> tuple[int, ...]:
    points: list[int] = []
    first_point = _row_content_start(body, 0)
    if first_point is not None and _needs_alignment_marker(body, first_point):
        points.append(first_point)

    env_depth = 0
    brace_depth = 0
    for token in tokenize_latex(body):
        if token.kind == "BEGIN_ENV":
            env_depth += 1
            continue
        if token.kind == "END_ENV":
            if env_depth > 0:
                env_depth -= 1
            continue
        if env_depth > 0:
            continue

        if token.kind == "TEXT":
            brace_depth = _brace_depth_after(token.value, brace_depth)
            continue
        if token.kind != "CONTROL_SYMBOL" or token.value != r"\\" or brace_depth != 0:
            continue

        point = _row_content_start(body, _linebreak_suffix_end(body, token))
        if point is not None and _needs_alignment_marker(body, point):
            points.append(point)

    return tuple(dict.fromkeys(points))


def _row_content_start(text: str, start: int) -> int | None:
    index = start
    while index < len(text):
        while index < len(text) and text[index].isspace():
            index += 1
        if not text.startswith("%", index):
            break
        index = _comment_end(text, index)
    return None if index >= len(text) else index


def _linebreak_suffix_end(text: str, token: LatexToken) -> int:
    index = _skip_horizontal_space(text, token.end)
    if index < len(text) and text[index] == "*":
        index = _skip_horizontal_space(text, index + 1)

    if index >= len(text) or text[index] != "[":
        return token.end

    option_end = _optional_argument_end(text, index)
    return token.end if option_end is None else option_end


def _skip_horizontal_space(text: str, start: int) -> int:
    index = start
    while index < len(text) and text[index] in " \t":
        index += 1
    return index


def _optional_argument_end(text: str, start: int) -> int | None:
    depth = 0
    index = start
    while index < len(text):
        char = text[index]
        if char == "\\":
            index += 2 if index + 1 < len(text) else 1
            continue
        if char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                return index + 1
        index += 1
    return None


def _needs_alignment_marker(text: str, index: int) -> bool:
    return text[index : index + 1] != "&"


def _brace_depth_after(text: str, depth: int) -> int:
    for char in text:
        if char == "{":
            depth += 1
            continue
        if char == "}" and depth > 0:
            depth -= 1
    return depth


def _comment_end(text: str, start: int) -> int:
    index = start + 1
    while index < len(text) and text[index] not in "\r\n":
        index += 1
    if index >= len(text):
        return index
    if text[index] == "\r" and index + 1 < len(text) and text[index + 1] == "\n":
        return index + 2
    return index + 1
