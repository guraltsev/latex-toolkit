"""Protect observable MyST Markdown command behavior.

The tests exercise public Markdown text transforms with the real MyST parser
and existing LaTeX math transforms.  File backup and clipboard boundaries are
covered by the shared command tests rather than duplicated here.
"""

from latex_toolkit.mdt_brace_args import transform_text as brace_math
from latex_toolkit.mdt_full_normalize import transform_text as normalize
from latex_toolkit.mdt_greek_latex2unicode import transform_text as greek_to_unicode
from latex_toolkit.mdt_greek_unicode2latex import transform_text as greek_to_latex
from latex_toolkit.mdt_math_latex2dollar import transform_text as to_dollar
from latex_toolkit.mdt_sentence_per_line import transform_text as sentences
from latex_toolkit.mdt_syntax_regularizer import transform_text as regularize


def test_markdown_normalization_formats_paragraphs_and_preserves_sensitive_source() -> None:
    """Supported prose is canonical while front matter, code, links, and lists survive exactly."""
    source = (
        "---\ntitle: A title\n---\n\n"
        "First wrapped\nparagraph. Second sentence.\n\n"
        "[a link](https://example.test/a b \"title\")\n\n"
        "- List wrapped\n  item.\n\n"
        "```python\n\\(not_math\\)\n```\n"
    )
    expected = (
        "---\ntitle: A title\n---\n\n"
        "First wrapped paragraph.\nSecond sentence.\n\n"
        "[a link](https://example.test/a b \"title\")\n\n"
        "- List wrapped\n  item.\n\n"
        "```python\n\\(not_math\\)\n```\n"
    )
    assert normalize(source) == expected
    assert normalize(expected) == expected


def test_math_commands_change_only_markdown_math_outside_protected_regions() -> None:
    """Delimiter, bracing, and Greek conversions leave identical protected spellings untouched."""
    source = (
        "Inline \\(x_1 + α\\).\n\n"
        "\\[\n\\frac12 + α\n\\]\n\n"
        "`\\(x_1 + α\\)`\n\n"
        "```tex\n\\(x_1 + α\\)\n```\n"
    )
    dollar = to_dollar(source)
    assert "$x_1 + α$" in dollar
    assert "$$\n\\frac12 + α\n$$" in dollar
    assert "`\\(x_1 + α\\)`" in dollar
    assert "```tex\n\\(x_1 + α\\)\n```" in dollar
    braced = brace_math(dollar)
    assert "$x_{1} + α$" in braced
    assert "\\frac{1}{2} + α" in braced
    assert "`\\(x_1 + α\\)`" in braced
    latex = greek_to_latex(braced)
    assert "$x_{1} + \\alpha$" in latex
    assert "\\frac{1}{2} + \\alpha" in latex
    assert greek_to_unicode(latex) == braced


def test_sentence_formatting_preserves_hard_breaks_and_newline_convention() -> None:
    """Hard-break paragraphs remain unchanged while CRLF prose receives CRLF sentence lines."""
    source = "First wrapped\r\nparagraph. Second sentence.\r\n\r\nHard break  \r\nremains.\r\n"
    assert sentences(source) == "First wrapped paragraph.\r\nSecond sentence.\r\n\r\nHard break  \r\nremains.\r\n"


def test_syntax_regularizer_does_not_cross_paragraph_boundaries() -> None:
    """Canonical wrapping changes soft line breaks only inside one ordinary paragraph."""
    assert regularize("One\nparagraph.\n\nOther\nparagraph.") == "One paragraph.\n\nOther paragraph."
