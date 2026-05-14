"""Literal math-mode LaTeX/Unicode conversion helpers.

The conversion intentionally stays lightweight. It rewrites only mutable
math-mode content, preserves comments verbatim, and when a balanced
``document`` environment is present limits edits to the document body.
"""

from __future__ import annotations

from pathlib import Path
import re

from .core import TexFile, read_tex_file
from .symbol_mappings import LATEX2UNICODE_MAP, UNICODE2LATEX_MAP

# Document markers bound conversions to body text when a full document exists.
_BEGIN_DOCUMENT_RE = re.compile(r"(?<!\\)\\begin\s*\{document\}")
_END_DOCUMENT_RE = re.compile(r"(?<!\\)\\end\s*\{document\}")

# Environment markers let math-mode tracking handle LaTeX environments.
_BEGIN_ENV_RE = re.compile(r"(?<!\\)\\begin\s*\{(?P<name>[^{}]+)\}")
_END_ENV_RE = re.compile(r"(?<!\\)\\end\s*\{(?P<name>[^{}]+)\}")

# These environments are treated as mutable math content.
_MATH_ENVIRONMENTS = {
    "displaymath",
    "math",
    "equation",
    "equation*",
    "align",
    "align*",
    "alignat",
    "alignat*",
    "flalign",
    "flalign*",
    "gather",
    "gather*",
    "multline",
    "multline*",
    "eqnarray",
    "eqnarray*",
    "split",
    "aligned",
    "alignedat",
    "gathered",
    "cases",
    "matrix",
    "pmatrix",
    "bmatrix",
    "Bmatrix",
    "vmatrix",
    "Vmatrix",
    "smallmatrix",
}

# Longer macros must be attempted first so prefixes such as ``\in`` do not win.
_LATEX_RULES = tuple(
    sorted((("\\" + name, value) for name, value in LATEX2UNICODE_MAP.items()), key=lambda item: -len(item[0]))
)


def convert_tex_file(source: str | Path | TexFile, *, reverse: bool = False) -> TexFile:
    """Convert mapped math symbols in ``source`` and return an anonymous ``TexFile``."""

    tex_file = _coerce_to_tex_file(source)
    return TexFile.anonymous(convert_text(tex_file.code, reverse=reverse))


def tex_to_unicode(source: str | Path | TexFile) -> TexFile:
    """Convert mapped LaTeX math macros to Unicode symbols."""

    return convert_tex_file(source, reverse=False)


def unicode_to_tex(source: str | Path | TexFile) -> TexFile:
    """Convert mapped Unicode math symbols to LaTeX macros."""

    return convert_tex_file(source, reverse=True)


def convert_text(text: str, *, reverse: bool = False) -> str:
    """Convert mapped math symbols inside raw LaTeX text."""

    preamble, begin_doc, body, end_doc, postamble = split_document_regions(text)
    if begin_doc and end_doc:
        converted_body = _convert_math_regions(body, reverse=reverse)
        return f"{preamble}{begin_doc}{converted_body}{end_doc}{postamble}"
    return _convert_math_regions(text, reverse=reverse)


def split_document_regions(text: str) -> tuple[str, str, str, str, str]:
    """Split ``text`` around a balanced ``document`` environment.

    Returns ``(preamble, begin_doc, body, end_doc, postamble)``. If a balanced
    pair is not found outside comments, the original text is returned as the
    preamble and the other fields are empty strings.
    """

    begin_match = _find_token_outside_comments(text, _BEGIN_DOCUMENT_RE)
    if begin_match is None:
        return text, "", "", "", ""

    end_match = _find_token_outside_comments(text, _END_DOCUMENT_RE, start=begin_match.end())
    if end_match is None:
        return text, "", "", "", ""

    return (
        text[: begin_match.start()],
        begin_match.group(0),
        text[begin_match.end() : end_match.start()],
        end_match.group(0),
        text[end_match.end() :],
    )


def _coerce_to_tex_file(source: str | Path | TexFile) -> TexFile:
    if isinstance(source, TexFile):
        return source
    return read_tex_file(source)


def _find_token_outside_comments(text: str, pattern: re.Pattern[str], *, start: int = 0) -> re.Match[str] | None:
    index = start
    in_comment = False

    while index < len(text):
        char = text[index]
        if in_comment:
            if char in "\r\n":
                in_comment = False
            index += 1
            continue

        if char == "%" and not _is_escaped(text, index):
            in_comment = True
            index += 1
            continue

        match = pattern.match(text, index)
        if match is not None:
            return match
        index += 1

    return None


def _convert_math_regions(text: str, *, reverse: bool) -> str:
    rendered: list[str] = []
    index = 0
    in_comment = False
    delimiter_stack: list[str] = []
    math_env_stack: list[str] = []

    while index < len(text):
        char = text[index]

        if in_comment:
            rendered.append(char)
            if char in "\r\n":
                in_comment = False
            index += 1
            continue

        if char == "%" and not _is_escaped(text, index):
            in_comment = True
            rendered.append(char)
            index += 1
            continue

        begin_env_match = _BEGIN_ENV_RE.match(text, index)
        if begin_env_match is not None:
            environment = begin_env_match.group("name")
            token = begin_env_match.group(0)
            rendered.append(token)
            if environment in _MATH_ENVIRONMENTS:
                math_env_stack.append(environment)
            index = begin_env_match.end()
            continue

        end_env_match = _END_ENV_RE.match(text, index)
        if end_env_match is not None:
            environment = end_env_match.group("name")
            token = end_env_match.group(0)
            rendered.append(token)
            if environment in _MATH_ENVIRONMENTS:
                _pop_matching_environment(math_env_stack, environment)
            index = end_env_match.end()
            continue

        delimiter = _math_delimiter_at(text, index)
        if delimiter is not None:
            rendered.append(delimiter)
            _update_delimiter_stack(delimiter_stack, delimiter)
            index += len(delimiter)
            continue

        if delimiter_stack or math_env_stack:
            converted, next_index = _convert_math_token(text, index, reverse=reverse)
            if converted is not None:
                rendered.append(converted)
                index = next_index
                continue

        rendered.append(char)
        index += 1

    return "".join(rendered)


def _math_delimiter_at(text: str, index: int) -> str | None:
    if text.startswith("\\(", index) and not _preceded_by_backslash(text, index):
        return "\\("
    if text.startswith("\\)", index) and not _preceded_by_backslash(text, index):
        return "\\)"
    if text.startswith("\\[", index) and not _preceded_by_backslash(text, index):
        return "\\["
    if text.startswith("\\]", index) and not _preceded_by_backslash(text, index):
        return "\\]"
    if text.startswith("$$", index) and not _is_escaped(text, index):
        return "$$"
    if text[index] == "$" and not _is_escaped(text, index):
        return "$"
    return None


def _convert_math_token(text: str, index: int, *, reverse: bool) -> tuple[str | None, int]:
    if reverse:
        character = text[index]
        if character in UNICODE2LATEX_MAP:
            return f"\\{UNICODE2LATEX_MAP[character]} ", index + 1
        return None, index

    for source, target in _LATEX_RULES:
        if not text.startswith(source, index):
            continue
        end = index + len(source)
        if source[-1].isalpha() and end < len(text) and text[end].isalpha():
            continue
        return target, end

    return None, index


def _update_delimiter_stack(stack: list[str], delimiter: str) -> None:
    if delimiter == "$$":
        if stack and stack[-1] == "$$":
            stack.pop()
            return
        if not stack or stack[-1] != "$":
            stack.append("$$")
        return

    if delimiter == "$":
        if stack and stack[-1] == "$":
            stack.pop()
            return
        if not stack or stack[-1] != "$$":
            stack.append("$")
        return

    if delimiter == "\\(":
        stack.append("\\)")
        return
    if delimiter == "\\[":
        stack.append("\\]")
        return
    if stack and stack[-1] == delimiter:
        stack.pop()


def _pop_matching_environment(stack: list[str], environment: str) -> None:
    for position in range(len(stack) - 1, -1, -1):
        if stack[position] == environment:
            del stack[position]
            return


def _is_escaped(text: str, index: int) -> bool:
    backslashes = 0
    lookback = index - 1
    while lookback >= 0 and text[lookback] == "\\":
        backslashes += 1
        lookback -= 1
    return backslashes % 2 == 1


def _preceded_by_backslash(text: str, index: int) -> bool:
    return index > 0 and text[index - 1] == "\\"
