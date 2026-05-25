"""Rewrite selected named ``\\ref`` phrases as ``\\cref`` or ``\\Cref`` calls."""

from __future__ import annotations

from pathlib import Path
import re

from latex_toolkit.lib.core import TexFile, read_tex_file

# Each rule maps one singular noun to the exact label prefixes that are eligible
# for replacement. Labels outside these prefix lists are left untouched.
_NOUN_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Proposition", ("prop:",)),
    ("Lemma", ("lem:", "lemma:")),
    ("Corollary", ("cor:", "corr:", "corrollary:")),
    ("Theorem", ("theorem:", "thm:")),
    ("Remark", ("rmk:", "rem:")),
)


def convert_tex_file(source: str | Path | TexFile) -> TexFile:
    """Convert ``source`` and return an anonymous :class:`TexFile`.

    Parameters
    ----------
    source : str or pathlib.Path or TexFile
        Source file path or already loaded TeX buffer.

    Returns
    -------
    TexFile
        Anonymous buffer with eligible named references rewritten as
        ``\\cref`` or ``\\Cref``.
    """

    tex_file = _coerce_to_tex_file(source)
    return TexFile.anonymous(convert_text(tex_file.code))


def convert_text(text: str) -> str:
    """Rewrite eligible named references in raw LaTeX text.

    Parameters
    ----------
    text : str
        LaTeX source text to transform.

    Returns
    -------
    str
        Source text where matching singular named ``\\ref`` phrases become
        ``\\cref`` or ``\\Cref``.
    """

    converted = text

    # Apply one literal phrase rule at a time so the behavior stays narrow and
    # easy to audit against the supported noun/prefix combinations.
    for noun, prefixes in _NOUN_RULES:
        converted = _rewrite_named_refs(converted, noun, prefixes, r"\Cref")
        converted = _rewrite_named_refs(converted, noun.lower(), prefixes, r"\cref")

    return converted


def _coerce_to_tex_file(source: str | Path | TexFile) -> TexFile:
    if isinstance(source, TexFile):
        return source
    return read_tex_file(source)


def _rewrite_named_refs(text: str, noun: str, prefixes: tuple[str, ...], cref: str) -> str:
    prefix_pattern = "|".join(re.escape(prefix) for prefix in prefixes)
    pattern = re.compile(
        rf"{re.escape(noun)}(?:~| )\\ref\{{(?P<label>(?:{prefix_pattern})[^}}]*)\}}"
    )

    # Replace the whole named phrase with a direct cleveref command while
    # preserving the original label text byte-for-byte.
    return pattern.sub(lambda match: f"{cref}{{{match.group('label')}}}", text)
