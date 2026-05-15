"""Brace single-token arguments passed to configured unary LaTeX macros.

The conversion preserves comments, leaves already braced arguments unchanged,
and limits edits to the document body when a balanced ``document`` environment
is present.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
import re
import tomllib

from .core import TexFile, read_tex_file
from .latex_parser import split_document_regions

# Default unary macros cover the local Fourier-transform shorthand and common
# one-argument math accents or decorators that are often written without braces.
DEFAULT_UNARY_MACROS: tuple[str, ...] = (
    "\\FT",
    "\\bar",
    "\\tilde",
    "\\dot",
    "\\ddot",
    "\\hat",
    "\\widehat",
    "\\widetilde",
    "\\vec",
    "\\overline",
    "\\underline",
    "\\breve",
    "\\check",
    "\\acute",
    "\\grave",
    "\\mathring",
    "\\mathfrak",
    "\\mf",
    "\\mathcal",
    "\\mc",
    "\\mathbb",
    "\\mb",
    "\\mbb",
    "\\mathscr",
    "\\ms",
    "\\mathbf",
    "\\mbf",
)

_CONTROL_WORD_RE = re.compile(r"\\[A-Za-z@]+")
_BARE_CONTROL_WORD_RE = re.compile(r"[A-Za-z@]+")
_NON_ARGUMENT_STARTS = frozenset("{}[]&#$^_")


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
        Macro commands whose next unbraced argument token should be wrapped in
        braces. Values may include or omit the leading backslash.

    Returns
    -------
    TexFile
        Anonymous buffer with configured unary macro arguments braced.
    """

    tex_file = _coerce_to_tex_file(source)
    return TexFile.anonymous(convert_text(tex_file.code, commands=commands))


def convert_text(text: str, *, commands: Iterable[str] | None = None) -> str:
    r"""Brace unbraced arguments of configured unary macros in raw LaTeX text.

    Parameters
    ----------
    text : str
        LaTeX source text to transform.
    commands : collections.abc.Iterable of str, optional
        Macro commands whose next unbraced argument token should be wrapped in
        braces. Defaults to :data:`DEFAULT_UNARY_MACROS`.

    Returns
    -------
    str
        Source text with matching unbraced macro arguments converted from forms
        such as ``\bar x`` to ``\bar{x}``.
    """

    active_commands = normalize_macro_commands(DEFAULT_UNARY_MACROS if commands is None else commands)
    if not active_commands:
        return text

    preamble, begin_doc, body, end_doc, postamble = split_document_regions(text)
    if begin_doc and end_doc:
        converted_body = _brace_macro_arguments(body, active_commands)
        return f"{preamble}{begin_doc}{converted_body}{end_doc}{postamble}"
    return _brace_macro_arguments(text, active_commands)


def load_macro_commands(path: str | Path) -> tuple[str, ...]:
    """Load macro commands from an absolute TOML configuration path.

    Parameters
    ----------
    path : str or pathlib.Path
        Absolute path to a TOML file with a top-level ``commands`` array. A
        top-level ``macros`` array is also accepted as an alias.

    Returns
    -------
    tuple of str
        Normalized macro commands with leading backslashes.

    Raises
    ------
    ValueError
        The path is not absolute or the TOML structure is invalid.
    """

    config_path = Path(path).expanduser()
    if not config_path.is_absolute():
        raise ValueError(f"Macro command file path must be absolute: {path}")

    data = tomllib.loads(config_path.read_text(encoding="utf-8"))
    command_values = data.get("commands", data.get("macros"))
    if command_values is None:
        raise ValueError("Macro command TOML must define a top-level 'commands' array.")
    if not isinstance(command_values, list) or not all(isinstance(item, str) for item in command_values):
        raise ValueError("Macro command TOML 'commands' value must be an array of strings.")
    return normalize_macro_commands(command_values)


def normalize_macro_commands(commands: Iterable[str]) -> tuple[str, ...]:
    """Return unique, validated macro commands with leading backslashes.

    Parameters
    ----------
    commands : collections.abc.Iterable of str
        Macro command names. Values may include or omit the leading backslash.

    Returns
    -------
    tuple of str
        Valid LaTeX control-word commands in first-seen order.

    Raises
    ------
    ValueError
        A value is empty or is not a LaTeX control-word command.
    """

    normalized: list[str] = []
    seen: set[str] = set()

    # Accept bare names for convenience, but validate the normalized command so
    # TOML typos fail before any source text is rewritten.
    for command in commands:
        stripped = command.strip()
        if not stripped:
            raise ValueError("Macro command names must not be empty.")
        if _BARE_CONTROL_WORD_RE.fullmatch(stripped):
            stripped = f"\\{stripped}"
        if _CONTROL_WORD_RE.fullmatch(stripped) is None:
            raise ValueError(f"Invalid LaTeX control-word command: {command!r}")
        if stripped not in seen:
            normalized.append(stripped)
            seen.add(stripped)

    return tuple(normalized)


def _coerce_to_tex_file(source: str | Path | TexFile) -> TexFile:
    if isinstance(source, TexFile):
        return source
    return read_tex_file(source)


def _brace_macro_arguments(text: str, commands: Iterable[str]) -> str:
    command_set = frozenset(commands)
    rendered: list[str] = []
    index = 0

    # Scan exact source text so comments and non-command fragments can be copied
    # byte-for-byte while command occurrences receive local rewrites.
    while index < len(text):
        char = text[index]

        if char == "%":
            end = _comment_end(text, index)
            rendered.append(text[index:end])
            index = end
            continue

        if char == "\\":
            control_word = _CONTROL_WORD_RE.match(text, index)
            if control_word is not None:
                command = control_word.group(0)
                if command in command_set:
                    replacement = _braced_macro_use(text, control_word.end(), command)
                    if replacement is not None:
                        converted, end = replacement
                        rendered.append(converted)
                        index = end
                        continue
                rendered.append(command)
                index = control_word.end()
                continue

            end = index + 2 if index + 1 < len(text) else index + 1
            rendered.append(text[index:end])
            index = end
            continue

        end = index + 1
        while end < len(text) and text[end] not in "\\%":
            end += 1
        rendered.append(text[index:end])
        index = end

    return "".join(rendered)


def _braced_macro_use(text: str, start: int, command: str) -> tuple[str, int] | None:
    argument_start = _skip_whitespace(text, start)
    if argument_start >= len(text):
        return None

    # Already braced arguments and structural TeX markers are left alone. This
    # also avoids rewriting common command-definition forms such as \newcommand\FT[1].
    char = text[argument_start]
    if char in _NON_ARGUMENT_STARTS or char == "%":
        return None
    if text.startswith("\\\\", argument_start):
        return None

    argument_end = _single_token_end(text, argument_start)
    if argument_end is None:
        return None
    return f"{command}{{{text[argument_start:argument_end]}}}", argument_end


def _single_token_end(text: str, start: int) -> int | None:
    if text[start] == "\\":
        control_word = _CONTROL_WORD_RE.match(text, start)
        if control_word is not None:
            return control_word.end()
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
