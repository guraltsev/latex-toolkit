"""Convert between dollar math delimiters and LaTeX bracket delimiters.

The conversion preserves comments, escaped dollar signs, and unmatched math
delimiters. When a balanced ``document`` environment is present, only the
document body is rewritten; otherwise the whole buffer is treated as a snippet.
"""

from __future__ import annotations

from pathlib import Path

from .core import TexFile, read_tex_file
from .latex_parser import LatexToken, split_document_regions, tokenize_latex


def convert_tex_file(source: str | Path | TexFile, *, reverse: bool = False) -> TexFile:
    """Convert math delimiters in ``source`` and return an anonymous buffer.

    Parameters
    ----------
    source : str or pathlib.Path or TexFile
        Source file path or already loaded TeX buffer.
    reverse : bool
        ``False`` rewrites dollar delimiters to bracket delimiters. ``True``
        rewrites bracket delimiters back to dollar delimiters.

    Returns
    -------
    TexFile
        Anonymous buffer with math delimiters rewritten.
    """

    tex_file = _coerce_to_tex_file(source)
    return TexFile.anonymous(convert_text(tex_file.code, reverse=reverse))


def dollar_math_to_brackets(source: str | Path | TexFile) -> TexFile:
    """Rewrite dollar math delimiters as bracket delimiters.

    Parameters
    ----------
    source : str or pathlib.Path or TexFile
        Source file path or already loaded TeX buffer.

    Returns
    -------
    TexFile
        Anonymous buffer with ``$`` and ``$$`` math delimiters rewritten.
    """

    return convert_tex_file(source, reverse=False)


def brackets_to_dollar_math(source: str | Path | TexFile) -> TexFile:
    """Rewrite bracket math delimiters as dollar delimiters.

    Parameters
    ----------
    source : str or pathlib.Path or TexFile
        Source file path or already loaded TeX buffer.

    Returns
    -------
    TexFile
        Anonymous buffer with ``\\( ... \\)`` and ``\\[ ... \\]`` delimiters
        rewritten.
    """

    return convert_tex_file(source, reverse=True)


def convert_text(text: str, *, reverse: bool = False) -> str:
    """Convert raw LaTeX text between dollar and bracket math delimiters.

    Parameters
    ----------
    text : str
        LaTeX source text to transform.
    reverse : bool
        ``False`` rewrites ``$ ... $`` as ``\\( ... \\)`` and ``$$ ... $$`` as
        ``\\[ ... \\]``. ``True`` performs the inverse rewrite.

    Returns
    -------
    str
        Source text with matched math delimiters rewritten.
    """

    preamble, begin_doc, body, end_doc, postamble = split_document_regions(text)
    if begin_doc and end_doc:
        return f"{preamble}{begin_doc}{_rewrite_delimiters(body, reverse=reverse)}{end_doc}{postamble}"
    return _rewrite_delimiters(text, reverse=reverse)


def _coerce_to_tex_file(source: str | Path | TexFile) -> TexFile:
    if isinstance(source, TexFile):
        return source
    return read_tex_file(source)


def _rewrite_delimiters(text: str, *, reverse: bool) -> str:
    tokens = tokenize_latex(text)
    replacements = _bracket_to_dollar_replacements(tokens) if reverse else _dollar_to_bracket_replacements(tokens)
    return _render_replacements(text, tokens, replacements)


def _dollar_to_bracket_replacements(tokens: tuple[LatexToken, ...]) -> dict[int, str]:
    replacements: dict[int, str] = {}
    active_token: LatexToken | None = None

    # Pair matching dollar tokens before replacing anything, so an unmatched
    # delimiter remains exactly as written.
    for token in tokens:
        if token.kind not in {"DOLLAR", "DOLLAR2"}:
            continue

        if active_token is None:
            active_token = token
            continue

        if token.kind != active_token.kind:
            continue

        if token.kind == "DOLLAR2":
            replacements[active_token.start] = r"\["
            replacements[token.start] = r"\]"
        else:
            replacements[active_token.start] = r"\("
            replacements[token.start] = r"\)"
        active_token = None

    return replacements


def _bracket_to_dollar_replacements(tokens: tuple[LatexToken, ...]) -> dict[int, str]:
    replacements: dict[int, str] = {}
    active_token: LatexToken | None = None
    expected_close = ""

    # Match modern delimiter pairs explicitly. Linebreak options like
    # ``\\[0.5em]`` are tokenized as a control symbol and are not touched here.
    for token in tokens:
        if active_token is None:
            if token.kind == "INLINE_OPEN_PAREN":
                active_token = token
                expected_close = "INLINE_CLOSE_PAREN"
            elif token.kind == "DISPLAY_OPEN":
                active_token = token
                expected_close = "DISPLAY_CLOSE"
            continue

        if token.kind != expected_close:
            continue

        if active_token.kind == "DISPLAY_OPEN":
            replacements[active_token.start] = "$$"
            replacements[token.start] = "$$"
        else:
            replacements[active_token.start] = "$"
            replacements[token.start] = "$"
        active_token = None
        expected_close = ""

    return replacements


def _render_replacements(text: str, tokens: tuple[LatexToken, ...], replacements: dict[int, str]) -> str:
    rendered: list[str] = []
    cursor = 0

    for token in tokens:
        replacement = replacements.get(token.start)
        if replacement is None:
            continue

        rendered.append(text[cursor : token.start])
        rendered.append(replacement)
        cursor = token.end

    rendered.append(text[cursor:])
    return "".join(rendered)
