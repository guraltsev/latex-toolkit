"""Delete configured unary macro calls together with their arguments."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from latex_toolkit.lib.core import TexFile, read_tex_file
from latex_toolkit.lib.latex_macro_config import (
    load_macro_commands,
    normalize_macro_commands,
)
from latex_toolkit.lib.latex_parser import split_document_regions

# TeXmacs exports can wrap content in project-local unary macros that should
# disappear entirely before the text is used as ordinary LaTeX.
DEFAULT_DELETED_MACROS: tuple[str, ...] = (r"\hide-preamble",)
_COMMAND_BOUNDARY_CHARS = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz@-")
_NON_ARGUMENT_STARTS = frozenset("[]&#$^_")


def convert_tex_file(
    source: str | Path | TexFile,
    *,
    commands: Iterable[str] | None = None,
) -> TexFile:
    """Convert ``source`` and return an anonymous :class:`TexFile`.

    Parameters
    ----------
    source : str or pathlib.Path or TexFile
        Source file path or already loaded TeX buffer.
    commands : collections.abc.Iterable of str, optional
        Macro commands whose unary applications should be removed completely.

    Returns
    -------
    TexFile
        Anonymous buffer with matching unary macro calls removed.
    """

    tex_file = _coerce_to_tex_file(source)
    return TexFile.anonymous(convert_text(tex_file.code, commands=commands))


def convert_text(text: str, *, commands: Iterable[str] | None = None) -> str:
    """Delete configured unary macro calls from raw LaTeX text.

    Parameters
    ----------
    text : str
        LaTeX source text to transform.
    commands : collections.abc.Iterable of str, optional
        Macro commands whose unary applications should be removed. Defaults to
        :data:`DEFAULT_DELETED_MACROS`.

    Returns
    -------
    str
        Source text with matching macro calls and their arguments removed.
    """

    active_commands = normalize_macro_commands(
        DEFAULT_DELETED_MACROS if commands is None else commands,
        allow_hyphenated=True,
    )
    if not active_commands:
        return text

    preamble, begin_doc, body, end_doc, postamble = split_document_regions(text)
    if begin_doc and end_doc:
        converted_body = _delete_macro_calls(body, active_commands)
        return f"{preamble}{begin_doc}{converted_body}{end_doc}{postamble}"
    return _delete_macro_calls(text, active_commands)


def load_delete_macro_commands(path: str | Path) -> tuple[str, ...]:
    """Load deletable macro commands from an absolute TOML configuration path.

    Parameters
    ----------
    path : str or pathlib.Path
        Absolute path to a TOML file with a top-level ``commands`` array. A
        top-level ``macros`` array is also accepted as an alias.

    Returns
    -------
    tuple of str
        Normalized macro commands with leading backslashes.
    """

    return load_macro_commands(path, allow_hyphenated=True)


def _coerce_to_tex_file(source: str | Path | TexFile) -> TexFile:
    if isinstance(source, TexFile):
        return source
    return read_tex_file(source)


def _delete_macro_calls(text: str, commands: tuple[str, ...]) -> str:
    rendered: list[str] = []
    index = 0

    # Copy exact source through comments and unmatched spans, and only drop
    # configured macro applications when a full unary argument is present.
    while index < len(text):
        if text[index] == "%":
            comment_end = _comment_end(text, index)
            rendered.append(text[index:comment_end])
            index = comment_end
            continue

        match = _match_command(text, index, commands)
        if match is None:
            rendered.append(text[index])
            index += 1
            continue

        command, command_end = match
        argument_end = _macro_argument_end(text, command_end)
        if argument_end is None:
            rendered.append(command)
            index = command_end
            continue
        index = argument_end

    return "".join(rendered)


def _match_command(text: str, index: int, commands: tuple[str, ...]) -> tuple[str, int] | None:
    if text[index] != "\\":
        return None

    # Prefer longer command names so ``\hide-preamble`` wins over any shorter
    # prefix that might also be configured.
    for command in sorted(commands, key=len, reverse=True):
        if not text.startswith(command, index):
            continue
        command_end = index + len(command)
        if command_end < len(text) and text[command_end] in _COMMAND_BOUNDARY_CHARS:
            continue
        return command, command_end
    return None


def _macro_argument_end(text: str, command_end: int) -> int | None:
    argument_start = _skip_whitespace(text, command_end)
    if argument_start >= len(text):
        return None
    if text[argument_start] == "%" or text.startswith("\\\\", argument_start):
        return None
    if text[argument_start] in _NON_ARGUMENT_STARTS:
        return None

    if text[argument_start] == "{":
        return _balanced_group_end(text, argument_start)
    return _single_token_end(text, argument_start)


def _balanced_group_end(text: str, start: int) -> int | None:
    depth = 0
    index = start

    # Track nested braces so whole braced arguments disappear even when they
    # contain inner groups or escaped control symbols.
    while index < len(text):
        char = text[index]
        if char == "%":
            index = _comment_end(text, index)
            continue
        if char == "\\":
            index += 2 if index + 1 < len(text) else 1
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index + 1
        index += 1

    return None


def _single_token_end(text: str, start: int) -> int | None:
    if text[start] == "\\":
        control_end = start + 1
        while control_end < len(text) and text[control_end] in _COMMAND_BOUNDARY_CHARS:
            control_end += 1
        if control_end > start + 1:
            return control_end
        if start + 1 < len(text):
            return start + 2
        return None
    return start + 1


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
