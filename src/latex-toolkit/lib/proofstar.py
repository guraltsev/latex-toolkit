r"""Helpers for converting between TeXmacs ``proof*`` and ``proof``.

The forward direction rewrites balanced ``\begin{proof*}{Title}`` /
``\end{proof*}`` environments as ``\begin{proof}[Title]`` / ``\end{proof}``
environments. The reverse direction rewrites titled ``proof`` environments
back to the TeXmacs ``proof*`` spelling.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent

from .core import TexFile, read_tex_file
from .latex_parser import (
    extract_environment_name,
    find_matching_environment_block,
    split_document_regions,
    tokenize_latex,
)


@dataclass(frozen=True, slots=True)
class _BraceGroup:
    """A balanced braced group has source span boundaries."""

    content_start: int
    content_end: int
    group_end: int


def convert_tex_file(source: str | Path | TexFile, *, reverse: bool = False) -> TexFile:
    """Convert ``source`` and return an anonymous :class:`TexFile`.

    Parameters
    ----------
    source : str or pathlib.Path or TexFile
        Source file path or already loaded TeX buffer.
    reverse : bool
        ``False`` rewrites titled ``proof*`` environments to ``proof``.
        ``True`` rewrites titled ``proof`` environments back to ``proof*``.

    Returns
    -------
    TexFile
        Anonymous buffer with converted proof environments.
    """

    tex_file = _coerce_to_tex_file(source)
    return TexFile.anonymous(convert_text(tex_file.code, reverse=reverse))


def proofstar_to_proof(source: str | Path | TexFile) -> TexFile:
    """Rewrite titled ``proof*`` environments as standard ``proof`` environments.

    Parameters
    ----------
    source : str or pathlib.Path or TexFile
        Source file path or already loaded TeX buffer.

    Returns
    -------
    TexFile
        Anonymous buffer with converted proof environments.
    """

    return convert_tex_file(source)


def proof_to_proofstar(source: str | Path | TexFile) -> TexFile:
    """Rewrite titled ``proof`` environments as TeXmacs ``proof*`` environments.

    Parameters
    ----------
    source : str or pathlib.Path or TexFile
        Source file path or already loaded TeX buffer.

    Returns
    -------
    TexFile
        Anonymous buffer with converted proof environments.
    """

    return convert_tex_file(source, reverse=True)


def convert_text(text: str, *, reverse: bool = False) -> str:
    """Convert raw LaTeX text between titled ``proof*`` and ``proof`` environments.

    Parameters
    ----------
    text : str
        LaTeX source text to transform.
    reverse : bool
        ``False`` rewrites titled ``proof*`` environments to ``proof``.
        ``True`` rewrites titled ``proof`` environments back to ``proof*``.

    Returns
    -------
    str
        Source text with document-body proof environments rewritten when a
        balanced ``document`` environment exists, otherwise with all matching
        environments rewritten.
    """

    preamble, begin_doc, body, end_doc, postamble = split_document_regions(text)
    active_text = body if begin_doc and end_doc else text
    converted = _rewrite_proof(active_text, reverse=reverse)
    if begin_doc and end_doc:
        return f"{preamble}{begin_doc}{converted}{end_doc}{postamble}"
    return converted


def _coerce_to_tex_file(source: str | Path | TexFile) -> TexFile:
    if isinstance(source, TexFile):
        return source
    return read_tex_file(source)


def _rewrite_proof(text: str, *, reverse: bool) -> str:
    if reverse:
        return _rewrite_proof_to_proofstar(text)
    return _rewrite_proofstar_to_proof(text)


def _rewrite_proofstar_to_proof(text: str) -> str:
    tokens = tokenize_latex(text)
    rendered: list[str] = []
    cursor = 0

    # Convert only complete titled proof blocks. Untitled, malformed, or
    # unmatched proof snippets are left byte-for-byte as they appeared.
    for token_index, token in enumerate(tokens):
        if token.start < cursor:
            continue
        if token.kind != "BEGIN_ENV" or extract_environment_name(token) != "proof*":
            continue

        title = _mandatory_group_after(text, token.end)
        if title is None:
            continue

        block = find_matching_environment_block(tokens, token_index, body_start=title.group_end)
        if block is None:
            continue

        title_text = text[title.content_start : title.content_end]
        body = _rewrite_proofstar_to_proof(text[block.body_start : block.body_end])
        rendered.append(text[cursor : token.start])
        rendered.append(rf"\begin{{proof}}[{title_text}]{dedent(body)}\end{{proof}}")
        cursor = tokens[block.close_token_index].end

    rendered.append(text[cursor:])
    return "".join(rendered)


def _rewrite_proof_to_proofstar(text: str) -> str:
    tokens = tokenize_latex(text)
    rendered: list[str] = []
    cursor = 0

    # Convert only complete titled proof blocks. Untitled proofs and malformed
    # optional arguments are preserved because their proof title is ambiguous.
    for token_index, token in enumerate(tokens):
        if token.start < cursor:
            continue
        if token.kind != "BEGIN_ENV" or extract_environment_name(token) != "proof":
            continue

        title = _optional_group_after(text, token.end)
        if title is None:
            continue

        block = find_matching_environment_block(tokens, token_index, body_start=title.group_end)
        if block is None:
            continue

        title_text = text[title.content_start : title.content_end]
        body = _rewrite_proof_to_proofstar(text[block.body_start : block.body_end])
        rendered.append(text[cursor : token.start])
        rendered.append(rf"\begin{{proof*}}{{{title_text}}}{body}\end{{proof*}}")
        cursor = tokens[block.close_token_index].end

    rendered.append(text[cursor:])
    return "".join(rendered)


def _mandatory_group_after(text: str, start: int) -> _BraceGroup | None:
    index = _skip_whitespace(text, start)
    if index >= len(text) or text[index] != "{":
        return None
    return _brace_group_at(text, index)


def _optional_group_after(text: str, start: int) -> _BraceGroup | None:
    index = _skip_whitespace(text, start)
    if index >= len(text) or text[index] != "[":
        return None
    return _bracket_group_at(text, index)


def _brace_group_at(text: str, start: int) -> _BraceGroup | None:
    depth = 1
    index = start + 1
    while index < len(text):
        char = text[index]
        if char == "\\":
            index += 2 if index + 1 < len(text) else 1
            continue
        if char == "%":
            index = _comment_end(text, index)
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return _BraceGroup(content_start=start + 1, content_end=index, group_end=index + 1)
        index += 1
    return None


def _bracket_group_at(text: str, start: int) -> _BraceGroup | None:
    depth = 1
    brace_depth = 0
    index = start + 1
    while index < len(text):
        char = text[index]
        if char == "\\":
            index += 2 if index + 1 < len(text) else 1
            continue
        if char == "%":
            index = _comment_end(text, index)
            continue
        if char == "{":
            brace_depth += 1
        elif char == "}" and brace_depth > 0:
            brace_depth -= 1
        elif char == "[" and brace_depth == 0:
            depth += 1
        elif char == "]" and brace_depth == 0:
            depth -= 1
            if depth == 0:
                return _BraceGroup(content_start=start + 1, content_end=index, group_end=index + 1)
        index += 1
    return None


def _skip_whitespace(text: str, start: int) -> int:
    index = start
    while index < len(text) and text[index].isspace():
        index += 1
    return index


def _comment_end(text: str, start: int) -> int:
    index = start + 1
    while index < len(text) and text[index] not in "\r\n":
        index += 1
    if index >= len(text):
        return index
    if text[index] == "\r" and index + 1 < len(text) and text[index + 1] == "\n":
        return index + 2
    return index + 1
