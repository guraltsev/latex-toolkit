r"""Rewrite TeXmacs ``\tmscript`` array scripts as ``\substack`` calls.

Balanced ``\tmscript{\begin{array}{c} ... \end{array}}`` constructs are
rewritten to ``\substack{...}``. Other ``\tmscript`` uses are left untouched so
non-centered arrays and malformed snippets remain source-preserving.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .core import TexFile, read_tex_file
from .latex_parser import (
    LatexToken,
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


@dataclass(frozen=True, slots=True)
class _ArrayArgument:
    """A centered array argument has a body source span."""

    body_start: int
    body_end: int


def convert_tex_file(source: str | Path | TexFile) -> TexFile:
    """Convert ``source`` and return an anonymous :class:`TexFile`.

    Parameters
    ----------
    source : str or pathlib.Path or TexFile
        Source file path or already loaded TeX buffer.

    Returns
    -------
    TexFile
        Anonymous buffer with TeXmacs script arrays rewritten.
    """

    tex_file = _coerce_to_tex_file(source)
    return TexFile.anonymous(convert_text(tex_file.code))


def tmscript_to_substack(source: str | Path | TexFile) -> TexFile:
    """Rewrite TeXmacs centered script arrays as ``\\substack`` calls.

    Parameters
    ----------
    source : str or pathlib.Path or TexFile
        Source file path or already loaded TeX buffer.

    Returns
    -------
    TexFile
        Anonymous buffer with converted ``\\tmscript`` constructs.
    """

    return convert_tex_file(source)


def convert_text(text: str) -> str:
    """Convert raw LaTeX text from TeXmacs script arrays to ``\\substack``.

    Parameters
    ----------
    text : str
        LaTeX source text to transform.

    Returns
    -------
    str
        Source text with document-body ``\\tmscript`` centered arrays rewritten
        when a balanced ``document`` environment exists, otherwise with all
        matching snippets rewritten.
    """

    preamble, begin_doc, body, end_doc, postamble = split_document_regions(text)
    active_text = body if begin_doc and end_doc else text
    converted = _rewrite_tmscript(active_text)
    if begin_doc and end_doc:
        return f"{preamble}{begin_doc}{converted}{end_doc}{postamble}"
    return converted


def _coerce_to_tex_file(source: str | Path | TexFile) -> TexFile:
    if isinstance(source, TexFile):
        return source
    return read_tex_file(source)


def _rewrite_tmscript(text: str) -> str:
    tokens = tokenize_latex(text)
    rendered: list[str] = []
    cursor = 0

    # Replace only complete TeXmacs script-array constructs. The scanner keeps
    # malformed or different ``\tmscript`` arguments exactly as they appeared.
    for token in tokens:
        if token.start < cursor:
            continue
        if token.kind != "CONTROL_WORD" or token.value != r"\tmscript":
            continue

        argument = _mandatory_group_after(text, token.end)
        if argument is None:
            continue

        array_argument = _centered_array_argument(text, tokens, argument)
        if array_argument is None:
            continue

        body = _rewrite_tmscript(text[array_argument.body_start : array_argument.body_end])
        rendered.append(text[cursor : token.start])
        rendered.append(rf"\substack{{{body}}}")
        cursor = argument.group_end

    rendered.append(text[cursor:])
    return "".join(rendered)


def _mandatory_group_after(text: str, start: int) -> _BraceGroup | None:
    index = _skip_whitespace(text, start)
    if index >= len(text) or text[index] != "{":
        return None
    return _brace_group_at(text, index)


def _centered_array_argument(
    text: str,
    tokens: tuple[LatexToken, ...],
    argument: _BraceGroup,
) -> _ArrayArgument | None:
    begin_index = _begin_array_token_index_at(tokens, _skip_whitespace(text, argument.content_start))
    if begin_index is None:
        return None

    begin_token = tokens[begin_index]
    column_group = _mandatory_group_after(text, begin_token.end)
    if column_group is None or column_group.group_end > argument.content_end:
        return None
    if text[column_group.content_start : column_group.content_end].strip() != "c":
        return None

    block = find_matching_environment_block(tokens, begin_index, body_start=column_group.group_end)
    if block is None:
        return None

    close_token = tokens[block.close_token_index]
    if close_token.end > argument.content_end:
        return None
    if _skip_whitespace(text, close_token.end) != argument.content_end:
        return None

    return _ArrayArgument(body_start=block.body_start, body_end=block.body_end)


def _begin_array_token_index_at(tokens: tuple[LatexToken, ...], start: int) -> int | None:
    for token_index, token in enumerate(tokens):
        if token.start < start:
            continue
        if token.start > start:
            return None
        if token.kind == "BEGIN_ENV" and extract_environment_name(token) == "array":
            return token_index
        return None
    return None


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
