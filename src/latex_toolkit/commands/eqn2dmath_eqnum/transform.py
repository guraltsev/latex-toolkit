r"""Helpers for converting between ``equation`` and ``\[\eqnum ... \]``.

The forward direction rewrites balanced ``equation`` environments as display
math whose body starts with the project-specific standalone ``\eqnum`` marker.
The reverse direction only rewrites display-math blocks whose bodies begin with
that standalone marker, leaving plain ``\[ ... \]`` blocks untouched.
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

# The local marker distinguishes numbered display math from plain display math.
_EQNUM_TOKEN = r"\eqnum"


def convert_tex_file(source: str | Path | TexFile, *, reverse: bool = False) -> TexFile:
    """Convert ``source`` and return an anonymous TeX buffer.

    Parameters
    ----------
    source : str, pathlib.Path, or TexFile
        Source file path or already loaded TeX buffer.
    reverse : bool
        ``False`` rewrites ``equation`` environments as numbered display math.
        ``True`` rewrites standalone ``\\eqnum`` display math back to
        ``equation``.

    Returns
    -------
    TexFile
        Anonymous buffer with converted numbered display-math source.
    """

    tex_file = _coerce_to_tex_file(source)
    return TexFile.anonymous(convert_text(tex_file.code, reverse=reverse))


def equation_to_eqnum_displaymath(source: str | Path | TexFile) -> TexFile:
    r"""Rewrite ``equation`` environments as ``\[\eqnum ... \]`` blocks.

    Parameters
    ----------
    source : str, pathlib.Path, or TexFile
        Source file path or already loaded TeX buffer.

    Returns
    -------
    TexFile
        Anonymous buffer with ``equation`` environments rewritten.
    """

    return convert_tex_file(source, reverse=False)


def eqnum_displaymath_to_equation(source: str | Path | TexFile) -> TexFile:
    r"""Rewrite ``\[\eqnum ... \]`` blocks as ``equation`` environments.

    Parameters
    ----------
    source : str, pathlib.Path, or TexFile
        Source file path or already loaded TeX buffer.

    Returns
    -------
    TexFile
        Anonymous buffer with standalone ``\eqnum`` display math rewritten.
    """

    return convert_tex_file(source, reverse=True)


def convert_text(text: str, *, reverse: bool = False) -> str:
    r"""Convert raw LaTeX text between ``equation`` and ``\[\eqnum ... \]``.

    Parameters
    ----------
    text : str
        LaTeX source text to transform.
    reverse : bool
        ``False`` rewrites ``equation`` environments as numbered display math.
        ``True`` rewrites standalone ``\eqnum`` display math back to
        ``equation``.

    Returns
    -------
    str
        Source text with the document body converted when a balanced
        ``document`` environment exists, otherwise with the whole buffer
        converted.
    """

    preamble, begin_doc, body, end_doc, postamble = split_document_regions(text)
    active_text = body if begin_doc and end_doc else text
    converted = _rewrite_displaymath(active_text) if reverse else _rewrite_equation(active_text)
    if begin_doc and end_doc:
        return f"{preamble}{begin_doc}{converted}{end_doc}{postamble}"
    return converted


def _coerce_to_tex_file(source: str | Path | TexFile) -> TexFile:
    if isinstance(source, TexFile):
        return source
    return read_tex_file(source)


def _rewrite_equation(text: str) -> str:
    tokens = tokenize_latex(text)
    rendered: list[str] = []
    cursor = 0

    for token_index, token in enumerate(tokens):
        if token.start < cursor:
            continue
        if token.kind != "BEGIN_ENV" or extract_environment_name(token) != "equation":
            continue

        block = find_matching_environment_block(tokens, token_index)
        if block is None:
            continue

        inner_body = _rewrite_equation(text[block.body_start : block.body_end])
        rendered.append(text[cursor : token.start])
        rendered.append(rf"\[{_prepend_eqnum(inner_body)}\]")
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
        stripped_body = _strip_leading_eqnum(inner_body)
        if stripped_body is None:
            continue

        rendered.append(text[cursor : token.start])
        rendered.append(rf"\begin{{equation}}{stripped_body}\end{{equation}}")
        cursor = tokens[block.close_token_index].end

    rendered.append(text[cursor:])
    return "".join(rendered)


def _prepend_eqnum(body: str) -> str:
    if not body:
        return _EQNUM_TOKEN
    if body[0].isspace():
        return f"{_EQNUM_TOKEN}{body}"
    return f"{_EQNUM_TOKEN} {body}"


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
