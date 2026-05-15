"""Shallow LaTeX tokenization and span discovery with exact source preservation.

The parser intentionally stays lightweight. It tokenizes raw source into exact
spans, groups mutable transform regions, and can match balanced environment
blocks without building a full TeX AST.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
import re


# Environments whose bodies count as math for token-region grouping.
MATH_ENVIRONMENT_NAMES: frozenset[str] = frozenset(
    {
        "equation",
        "equation*",
        "align",
        "align*",
        "alignat",
        "alignat*",
        "aligned",
        "alignedat",
        "gather",
        "gather*",
        "gathered",
        "multline",
        "multline*",
        "math",
        "displaymath",
        "flalign",
        "flalign*",
        "eqnarray",
        "eqnarray*",
        "split",
        "cases",
        "matrix",
        "pmatrix",
        "bmatrix",
        "Bmatrix",
        "vmatrix",
        "Vmatrix",
        "smallmatrix",
    }
)

# Token patterns preserve exact source spans for environments and controls.
_ENVIRONMENT_TOKEN_RE = re.compile(r"\\(begin|end)\{([^}]+)\}")
_BEGIN_ENV_SCAN_RE = re.compile(r"\\begin\{[^}]+\}")
_END_ENV_SCAN_RE = re.compile(r"\\end\{[^}]+\}")
_CONTROL_WORD_RE = re.compile(r"\\[A-Za-z]+")
_CONTROL_WORD_SUFFIX_RE = re.compile(r".*\\[A-Za-z]+$")

# Mutable token kinds can be grouped and rewritten by literal transform passes.
_MUTABLE_TOKEN_KINDS = frozenset({"CONTROL_WORD", "TEXT"})

# Structural tokens change parser state and are never rewritten as plain text.
_STRUCTURAL_TOKEN_KINDS = frozenset(
    {
        "BEGIN_ENV",
        "END_ENV",
        "DISPLAY_OPEN",
        "DISPLAY_CLOSE",
        "INLINE_OPEN_PAREN",
        "INLINE_CLOSE_PAREN",
        "DOLLAR2",
        "DOLLAR",
    }
)


@dataclass(frozen=True, slots=True)
class LatexToken:
    """Exact token emitted by :func:`tokenize_latex`."""

    kind: str
    value: str
    start: int
    end: int


@dataclass(frozen=True, slots=True)
class TransformRegion:
    """Contiguous span suitable for literal rewriting decisions."""

    kind: str
    text: str
    start: int
    end: int
    in_math: bool


@dataclass(frozen=True, slots=True)
class DisplayMathBlock:
    """Balanced ``\\[ ... \\]`` block discovered in a token stream."""

    open_token_index: int
    close_token_index: int
    body_start: int
    body_end: int


@dataclass(frozen=True, slots=True)
class EnvironmentBlock:
    """Balanced ``\\begin{...}`` / ``\\end{...}`` block discovered in tokens."""

    env_name: str
    open_token_index: int
    close_token_index: int
    body_start: int
    body_end: int


def tokenize_latex(text: str) -> tuple[LatexToken, ...]:
    """Tokenize LaTeX source into exact source-preserving tokens."""

    tokens: list[LatexToken] = []
    index = 0
    text_length = len(text)

    while index < text_length:
        char = text[index]

        if char == "%":
            end = _comment_end(text, index)
            tokens.append(LatexToken(kind="COMMENT", value=text[index:end], start=index, end=end))
            index = end
            continue

        if text.startswith("\\begin{", index):
            match = _BEGIN_ENV_SCAN_RE.match(text, index)
            if match is not None:
                tokens.append(LatexToken(kind="BEGIN_ENV", value=match.group(0), start=index, end=match.end()))
                index = match.end()
                continue

        if text.startswith("\\end{", index):
            match = _END_ENV_SCAN_RE.match(text, index)
            if match is not None:
                tokens.append(LatexToken(kind="END_ENV", value=match.group(0), start=index, end=match.end()))
                index = match.end()
                continue

        if text.startswith("\\[", index):
            tokens.append(LatexToken(kind="DISPLAY_OPEN", value="\\[", start=index, end=index + 2))
            index += 2
            continue
        if text.startswith("\\]", index):
            tokens.append(LatexToken(kind="DISPLAY_CLOSE", value="\\]", start=index, end=index + 2))
            index += 2
            continue
        if text.startswith("\\(", index):
            tokens.append(LatexToken(kind="INLINE_OPEN_PAREN", value="\\(", start=index, end=index + 2))
            index += 2
            continue
        if text.startswith("\\)", index):
            tokens.append(LatexToken(kind="INLINE_CLOSE_PAREN", value="\\)", start=index, end=index + 2))
            index += 2
            continue
        if text.startswith("$$", index):
            tokens.append(LatexToken(kind="DOLLAR2", value="$$", start=index, end=index + 2))
            index += 2
            continue
        if char == "$":
            tokens.append(LatexToken(kind="DOLLAR", value="$", start=index, end=index + 1))
            index += 1
            continue

        if char == "\\":
            match = _CONTROL_WORD_RE.match(text, index)
            if match is not None:
                tokens.append(LatexToken(kind="CONTROL_WORD", value=match.group(0), start=index, end=match.end()))
                index = match.end()
                continue
            if index + 1 < text_length:
                end = index + 2
                tokens.append(LatexToken(kind="CONTROL_SYMBOL", value=text[index:end], start=index, end=end))
                index = end
                continue
            tokens.append(LatexToken(kind="BACKSLASH", value="\\", start=index, end=index + 1))
            index += 1
            continue

        end = index + 1
        while end < text_length and text[end] not in "\\$%":
            end += 1
        tokens.append(LatexToken(kind="TEXT", value=text[index:end], start=index, end=end))
        index = end

    return tuple(tokens)


def extract_environment_name(token: LatexToken) -> str | None:
    """Extract the environment name from a begin/end environment token."""

    if token.kind not in {"BEGIN_ENV", "END_ENV"}:
        return None
    match = _ENVIRONMENT_TOKEN_RE.fullmatch(token.value)
    return None if match is None else match.group(2)


def split_document_regions(text: str) -> tuple[str, str, str, str, str]:
    """Split a document into preamble, body, and postamble regions."""

    tokens = tokenize_latex(text)
    begin_token: LatexToken | None = None
    end_token: LatexToken | None = None

    for token in tokens:
        if token.kind == "BEGIN_ENV" and extract_environment_name(token) == "document":
            begin_token = token
            break
    if begin_token is None:
        return text, "", "", "", ""

    for token in tokens:
        if token.start < begin_token.end:
            continue
        if token.kind == "END_ENV" and extract_environment_name(token) == "document":
            end_token = token
            break
    if end_token is None:
        return text, "", "", "", ""

    return (
        text[: begin_token.start],
        begin_token.value,
        text[begin_token.end : end_token.start],
        end_token.value,
        text[end_token.end :],
    )


def iter_transform_regions(
    text: str,
    *,
    math_environment_names: Iterable[str] | None = None,
) -> tuple[TransformRegion, ...]:
    """Group tokenized text into mutable and immutable transform regions."""

    active_math_envs = frozenset(math_environment_names or MATH_ENVIRONMENT_NAMES)
    tokens = tokenize_latex(text)
    regions: list[TransformRegion] = []
    math_stack: list[str] = []
    buffered_tokens: list[LatexToken] = []
    buffered_in_math = False

    def flush_buffer() -> None:
        nonlocal buffered_tokens, buffered_in_math
        if not buffered_tokens:
            return
        regions.append(
            TransformRegion(
                kind="mutable",
                text="".join(token.value for token in buffered_tokens),
                start=buffered_tokens[0].start,
                end=buffered_tokens[-1].end,
                in_math=buffered_in_math,
            )
        )
        buffered_tokens = []

    for token in tokens:
        in_math_before_token = bool(math_stack)
        if token.kind in _MUTABLE_TOKEN_KINDS:
            if (
                buffered_tokens
                and buffered_in_math == in_math_before_token
                and token.start == buffered_tokens[-1].end
            ):
                buffered_tokens.append(token)
            else:
                flush_buffer()
                buffered_in_math = in_math_before_token
                buffered_tokens = [token]
            continue

        flush_buffer()
        regions.append(
            TransformRegion(
                kind=_region_kind_for_token(token),
                text=token.value,
                start=token.start,
                end=token.end,
                in_math=in_math_before_token,
            )
        )
        _update_math_stack(math_stack, token, math_environment_names=active_math_envs)

    flush_buffer()
    return tuple(regions)


def find_matching_environment_block(
    tokens: Sequence[LatexToken],
    open_token_index: int,
    *,
    body_start: int | None = None,
) -> EnvironmentBlock | None:
    """Find the balanced environment block starting at ``open_token_index``."""

    if open_token_index < 0 or open_token_index >= len(tokens):
        return None
    open_token = tokens[open_token_index]
    env_name = extract_environment_name(open_token)
    if open_token.kind != "BEGIN_ENV" or env_name is None:
        return None

    depth = 1
    for token_index in range(open_token_index + 1, len(tokens)):
        token = tokens[token_index]
        token_env_name = extract_environment_name(token)
        if token.kind == "BEGIN_ENV" and token_env_name == env_name:
            depth += 1
            continue
        if token.kind == "END_ENV" and token_env_name == env_name:
            depth -= 1
            if depth == 0:
                return EnvironmentBlock(
                    env_name=env_name,
                    open_token_index=open_token_index,
                    close_token_index=token_index,
                    body_start=open_token.end if body_start is None else body_start,
                    body_end=token.start,
                )
    return None


def find_matching_displaymath_block(tokens: Sequence[LatexToken], open_token_index: int) -> DisplayMathBlock | None:
    """Find the balanced ``\\[ ... \\]`` block starting at ``open_token_index``."""

    if open_token_index < 0 or open_token_index >= len(tokens):
        return None
    open_token = tokens[open_token_index]
    if open_token.kind != "DISPLAY_OPEN":
        return None

    depth = 1
    for token_index in range(open_token_index + 1, len(tokens)):
        token = tokens[token_index]
        if token.kind == "DISPLAY_OPEN":
            depth += 1
            continue
        if token.kind == "DISPLAY_CLOSE":
            depth -= 1
            if depth == 0:
                return DisplayMathBlock(
                    open_token_index=open_token_index,
                    close_token_index=token_index,
                    body_start=open_token.end,
                    body_end=token.start,
                )
    return None


def requires_control_word_boundary(source: str) -> bool:
    """Return whether a replacement source needs a trailing letter boundary."""

    return bool(_CONTROL_WORD_SUFFIX_RE.match(source))


def _comment_end(text: str, start: int) -> int:
    index = start + 1
    while index < len(text) and text[index] not in "\r\n":
        index += 1
    if index >= len(text):
        return index
    if text[index] == "\r" and index + 1 < len(text) and text[index + 1] == "\n":
        return index + 2
    return index + 1


def _region_kind_for_token(token: LatexToken) -> str:
    if token.kind == "COMMENT":
        return "comment"
    if token.kind == "CONTROL_SYMBOL":
        return "control_symbol"
    if token.kind == "BACKSLASH":
        return "backslash"
    if token.kind in _STRUCTURAL_TOKEN_KINDS:
        return "structural"
    return "mutable"


def _update_math_stack(
    math_stack: list[str],
    token: LatexToken,
    *,
    math_environment_names: Sequence[str] | frozenset[str],
) -> None:
    env_name = extract_environment_name(token)
    if token.kind == "BEGIN_ENV" and env_name in math_environment_names:
        math_stack.append(f"env:{env_name}")
        return
    if token.kind == "END_ENV" and env_name in math_environment_names:
        if math_stack and math_stack[-1] == f"env:{env_name}":
            math_stack.pop()
        return
    if token.kind == "DISPLAY_OPEN":
        math_stack.append("display")
        return
    if token.kind == "DISPLAY_CLOSE":
        if math_stack and math_stack[-1] == "display":
            math_stack.pop()
        return
    if token.kind == "INLINE_OPEN_PAREN":
        math_stack.append("inline-paren")
        return
    if token.kind == "INLINE_CLOSE_PAREN":
        if math_stack and math_stack[-1] == "inline-paren":
            math_stack.pop()
        return
    if token.kind == "DOLLAR2":
        if math_stack and math_stack[-1] == "dollar2":
            math_stack.pop()
        else:
            math_stack.append("dollar2")
        return
    if token.kind == "DOLLAR":
        if math_stack and math_stack[-1] == "dollar":
            math_stack.pop()
        else:
            math_stack.append("dollar")
