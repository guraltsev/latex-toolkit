"""Load and validate configurable LaTeX macro command lists."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
import re
import tomllib

_BARE_CONTROL_WORD_RE = re.compile(r"[A-Za-z@]+")
_BARE_HYPHENATED_CONTROL_WORD_RE = re.compile(r"[A-Za-z@][A-Za-z@-]*")
_CONTROL_WORD_RE = re.compile(r"\\[A-Za-z@]+")
_HYPHENATED_CONTROL_WORD_RE = re.compile(r"\\[A-Za-z@][A-Za-z@-]*")


def load_macro_commands(
    path: str | Path,
    *,
    allow_hyphenated: bool = False,
) -> tuple[str, ...]:
    """Load macro commands from an absolute TOML configuration path.

    Parameters
    ----------
    path : str or pathlib.Path
        Absolute path to a TOML file with a top-level ``commands`` array. A
        top-level ``macros`` array is also accepted as an alias.
    allow_hyphenated : bool, optional
        Whether command names such as ``\\hide-preamble`` are accepted.

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
    return normalize_macro_commands(command_values, allow_hyphenated=allow_hyphenated)


def normalize_macro_commands(
    commands: Iterable[str],
    *,
    allow_hyphenated: bool = False,
) -> tuple[str, ...]:
    """Return unique, validated macro commands with leading backslashes.

    Parameters
    ----------
    commands : collections.abc.Iterable of str
        Macro command names. Values may include or omit the leading backslash.
    allow_hyphenated : bool, optional
        Whether command names such as ``\\hide-preamble`` are accepted.

    Returns
    -------
    tuple of str
        Valid LaTeX-style control-word commands in first-seen order.

    Raises
    ------
    ValueError
        A value is empty or is not a valid command name.
    """

    bare_pattern = _BARE_HYPHENATED_CONTROL_WORD_RE if allow_hyphenated else _BARE_CONTROL_WORD_RE
    command_pattern = _HYPHENATED_CONTROL_WORD_RE if allow_hyphenated else _CONTROL_WORD_RE

    normalized: list[str] = []
    seen: set[str] = set()

    # Accept bare names for convenience, but validate the normalized command so
    # configuration typos fail before any source text is rewritten.
    for command in commands:
        stripped = command.strip()
        if not stripped:
            raise ValueError("Macro command names must not be empty.")
        if bare_pattern.fullmatch(stripped):
            stripped = f"\\{stripped}"
        if command_pattern.fullmatch(stripped) is None:
            raise ValueError(f"Invalid LaTeX control-word command: {command!r}")
        if stripped not in seen:
            normalized.append(stripped)
            seen.add(stripped)

    return tuple(normalized)
