r"""Helpers for converting between ``equation*`` and plain display math.

The forward direction rewrites balanced ``equation*`` environments as exact
``\[ ... \]`` blocks. The reverse direction only rewrites *plain* display-math
blocks back to ``equation*`` and intentionally leaves ``\eqnum``-prefixed
blocks untouched so the numbered-equation workflow can handle them.
"""

from __future__ import annotations

from pathlib import Path

from latex_toolkit.lib.core import TexFile, read_tex_file
from latex_toolkit.lib.latex_parser import (
    extract_environment_name,
    find_matching_displaymath_block,
    find_matching_environment_block,
    split_document_regions,
    tokenize_latex,
)

# Numbered-display blocks belong to the numbered-equation conversion workflow.
_EQNUM_TOKEN = r"\eqnum"


def convert_tex_file(source: str | Path | TexFile, *, reverse: bool = False) -> TexFile:
    """Convert ``source`` and return an anonymous :class:`TexFile`."""

    tex_file = _coerce_to_tex_file(source)
    return TexFile.anonymous(convert_text(tex_file.code, reverse=reverse))


def equation_star_to_displaymath(source: str | Path | TexFile) -> TexFile:
    r"""Rewrite ``equation*`` environments as ``\[ ... \]`` blocks."""

    return convert_tex_file(source, reverse=False)


def displaymath_to_equation_star(source: str | Path | TexFile) -> TexFile:
    r"""Rewrite plain ``\[ ... \]`` blocks as ``equation*`` environments."""

    return convert_tex_file(source, reverse=True)


def convert_text(text: str, *, reverse: bool = False) -> str:
    """Convert raw LaTeX text between ``equation*`` and plain display math."""

    preamble, begin_doc, body, end_doc, postamble = split_document_regions(text)
    active_text = body if begin_doc and end_doc else text
    converted = _rewrite_displaymath(active_text) if reverse else _rewrite_equation_star(active_text)
    if begin_doc and end_doc:
        return f"{preamble}{begin_doc}{converted}{end_doc}{postamble}"
    return converted


def _coerce_to_tex_file(source: str | Path | TexFile) -> TexFile:
    if isinstance(source, TexFile):
        return source
    return read_tex_file(source)


def _rewrite_equation_star(text: str) -> str:
    tokens = tokenize_latex(text)
    rendered: list[str] = []
    cursor = 0

    for token_index, token in enumerate(tokens):
        if token.start < cursor:
            continue
        if token.kind != "BEGIN_ENV" or extract_environment_name(token) != "equation*":
            continue

        block = find_matching_environment_block(tokens, token_index)
        if block is None:
            continue

        inner_body = _rewrite_equation_star(text[block.body_start : block.body_end])
        rendered.append(text[cursor : token.start])
        rendered.append(rf"\[{inner_body}\]")
        cursor = tokens[block.close_token_index].end

    rendered.append(text[cursor:])
    return "".join(rendered)


def _rewrite_displaymath(text: str) -> str:
    tokens = tokenize_latex(text)
    rendered: list[str] = []
    cursor = 0

    for token_index, token in enumerate(tokens):
        if token.start < cursor:
            continue
        if token.kind != "DISPLAY_OPEN":
            continue

        block = find_matching_displaymath_block(tokens, token_index)
        if block is None:
            continue

        inner_body = _rewrite_displaymath(text[block.body_start : block.body_end])
        if _strip_leading_eqnum(inner_body) is not None:
            continue

        rendered.append(text[cursor : token.start])
        rendered.append(rf"\begin{{equation*}}{inner_body}\end{{equation*}}")
        cursor = tokens[block.close_token_index].end

    rendered.append(text[cursor:])
    return "".join(rendered)


def _strip_leading_eqnum(body: str) -> str | None:
    index = 0
    while index < len(body) and body[index].isspace():
        index += 1
    if not body.startswith(_EQNUM_TOKEN, index):
        return None
    token_end = index + len(_EQNUM_TOKEN)
    if token_end < len(body) and body[token_end].isalpha():
        return None
    return body[token_end:]
