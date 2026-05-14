"""Helpers for converting between ``aligned`` blocks and ``\\ba`` / ``\\ea``.

The forward direction compresses only exact ``\\begin{aligned}[t]`` /
``\\end{aligned}`` blocks. The reverse direction expands literal ``\\ba`` and
``\\ea`` shorthands while preserving comments and structural tokens.
"""

from __future__ import annotations

from pathlib import Path
import re

from .core import TexFile, read_tex_file
from .latex_parser import (
    extract_environment_name,
    find_matching_environment_block,
    iter_transform_regions,
    requires_control_word_boundary,
    split_document_regions,
    tokenize_latex,
)

# Only exact ``[t]`` options are compressed into the local shorthand.
_ALIGNED_OPTION_RE = re.compile(r"(?:[ \t\r\n]*)\[t\]")

# Reverse conversion is a literal, boundary-aware replacement pass.
_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    (r"\ba", r"\begin{aligned}[t]"),
    (r"\ea", r"\end{aligned}"),
)


def convert_tex_file(source: str | Path | TexFile, *, reverse: bool = False) -> TexFile:
    """Convert ``source`` and return an anonymous :class:`TexFile`."""

    tex_file = _coerce_to_tex_file(source)
    return TexFile.anonymous(convert_text(tex_file.code, reverse=reverse))


def aligned_to_baea(source: str | Path | TexFile) -> TexFile:
    """Compress explicit ``aligned`` environments into ``\\ba`` / ``\\ea``."""

    return convert_tex_file(source, reverse=False)


def baea_to_aligned(source: str | Path | TexFile) -> TexFile:
    """Expand ``\\ba`` / ``\\ea`` shorthands into ``aligned`` environments."""

    return convert_tex_file(source, reverse=True)


def convert_text(text: str, *, reverse: bool = False) -> str:
    """Convert raw LaTeX text between the two representations."""

    preamble, begin_doc, body, end_doc, postamble = split_document_regions(text)
    converted = _expand_shorthand(body if begin_doc and end_doc else text) if reverse else _compress_aligned(body if begin_doc and end_doc else text)
    if begin_doc and end_doc:
        return f"{preamble}{begin_doc}{converted}{end_doc}{postamble}"
    return converted


def _coerce_to_tex_file(source: str | Path | TexFile) -> TexFile:
    if isinstance(source, TexFile):
        return source
    return read_tex_file(source)


def _compress_aligned(text: str) -> str:
    tokens = tokenize_latex(text)
    rendered: list[str] = []
    cursor = 0

    for token_index, token in enumerate(tokens):
        if token.start < cursor:
            continue
        if token.kind != "BEGIN_ENV" or extract_environment_name(token) != "aligned":
            continue

        body_start = _aligned_body_start(text, token.end)
        if body_start is None:
            continue

        block = find_matching_environment_block(tokens, token_index, body_start=body_start)
        if block is None:
            continue

        inner_body = _compress_aligned(text[block.body_start : block.body_end])
        close_token = tokens[block.close_token_index]
        next_char = text[close_token.end : close_token.end + 1]

        rendered.append(text[cursor : token.start])
        rendered.append(_render_baea(inner_body, next_char))
        cursor = close_token.end

    rendered.append(text[cursor:])
    return "".join(rendered)


def _expand_shorthand(text: str) -> str:
    rendered: list[str] = []
    for region in iter_transform_regions(text):
        if region.kind != "mutable":
            rendered.append(region.text)
            continue
        rendered.append(_apply_literal_replacements(region.text))
    return "".join(rendered)


def _aligned_body_start(text: str, start: int) -> int | None:
    match = _ALIGNED_OPTION_RE.match(text, start)
    return None if match is None else match.end()


def _render_baea(body: str, next_char: str) -> str:
    opening = r"\ba"
    closing = r"\ea"
    if body[:1].isalpha():
        opening += " "
    if next_char.isalpha():
        closing += " "
    return f"{opening}{body}{closing}"


def _apply_literal_replacements(text: str) -> str:
    output: list[str] = []
    index = 0
    while index < len(text):
        for source, target in _REPLACEMENTS:
            if not text.startswith(source, index):
                continue
            end = index + len(source)
            if requires_control_word_boundary(source) and end < len(text) and text[end].isalpha():
                continue
            output.append(target)
            index = end
            break
        else:
            output.append(text[index])
            index += 1
    return "".join(output)
