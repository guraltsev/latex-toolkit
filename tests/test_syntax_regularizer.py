r"""Protect user-visible LaTeX syntax regularization behavior.

The tests exercise the real pylatexenc parsing boundary through the public
text transformation. File and clipboard workflows and private helper layout
are outside this module's scope.
"""

import pytest

from syntax_regularizer import transform_text


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("$1+1=\n2$", "$1+1=2$"),
        ("\\(1+1=\n2\\)", r"\(1+1=2\)"),
        ("$a\r\n  +b$", "$a+b$"),
    ],
    ids=["dollar", "parenthesized", "crlf-with-indentation"],
)
def test_uncommented_inline_math_has_no_physical_newlines(
    source: str, expected: str
) -> None:
    """Every physical newline and its line indentation leave inline math."""
    assert transform_text(source) == expected


@pytest.mark.parametrize(
    "source",
    [
        "$1+1= %this is stupid\n2$",
        "\\(1+1= % keep this line\n  2\\)",
    ],
    ids=["dollar", "parenthesized"],
)
def test_inline_math_with_a_comment_is_byte_identical(source: str) -> None:
    """An unescaped comment preserves the complete inline math source."""
    assert transform_text(source) == source


def test_escaped_percent_does_not_protect_inline_math_wrapping() -> None:
    """An escaped percent remains math content rather than starting a comment."""
    assert transform_text("$50\\%\n+1$") == "$50\\%+1$"


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            r"Before \begin{equation}x=1\end{equation} after",
            "Before\n\\begin{equation}\nx=1\n\\end{equation}\nafter",
        ),
        (r"Before \[x=1\] after", "Before\n\\[\nx=1\n\\]\nafter"),
        (
            r"\begin{align}a&=b\end{align}",
            "\\begin{align}\na&=b\n\\end{align}",
        ),
        (
            r"\begin{gather}a=b\end{gather}",
            "\\begin{gather}\na=b\n\\end{gather}",
        ),
        (
            r"\begin{alignat}{2}a&=b\end{alignat}",
            "\\begin{alignat}{2}\na&=b\n\\end{alignat}",
        ),
        (
            r"\begin{align}\begin{split}a&=b\end{split}\end{align}",
            (
                "\\begin{align}\n\\begin{split}\na&=b\n"
                "\\end{split}\n\\end{align}"
            ),
        ),
    ],
    ids=["equation", "brackets", "align", "gather", "alignat", "nested-split"],
)
def test_display_delimiters_are_isolated_without_blank_lines(
    source: str, expected: str
) -> None:
    """Display openers and closers receive exactly the needed physical breaks."""
    transformed = transform_text(source)

    assert transformed == expected
    assert "\n\n" not in transformed


def test_existing_display_layout_and_paragraph_breaks_are_preserved() -> None:
    """Already isolated display delimiters do not gain additional newlines."""
    source = "Paragraph.\n\n\\[\n  x=1\n\\]\n\nNext paragraph."

    assert transform_text(source) == source


def test_only_ordinary_text_loses_beginning_of_line_indentation() -> None:
    """Text indentation is removed while math, verbatim, and tables stay exact."""
    source = (
        "  Ordinary text.\n"
        "\\begin{equation}\n  x=1\n\\end{equation}\n"
        "\\begin{verbatim}\n  literal text\n\\end{verbatim}\n"
        "\\begin{table}\n  \\begin{tabular}{c}\n    cell\\\\\n"
        "  \\end{tabular}\n\\end{table}\n"
        "    More text."
    )

    assert transform_text(source) == (
        "Ordinary text.\n"
        "\\begin{equation}\n  x=1\n\\end{equation}\n"
        "\\begin{verbatim}\n  literal text\n\\end{verbatim}\n"
        "\\begin{table}\n  \\begin{tabular}{c}\n    cell\\\\\n"
        "  \\end{tabular}\n\\end{table}\n"
        "More text."
    )


def test_indentation_before_math_delimiters_is_removed() -> None:
    """Math protects internal indentation but not whitespace before its opener."""
    source = (
        "  \\(x\\)\n"
        "  \\[\n"
        "    x=1\n"
        "\\]\n"
        "  \\begin{equation}\n"
        "    y=2\n"
        "\\end{equation}"
    )

    assert transform_text(source) == (
        "\\(x\\)\n"
        "\\[\n"
        "    x=1\n"
        "\\]\n"
        "\\begin{equation}\n"
        "    y=2\n"
        "\\end{equation}"
    )


@pytest.mark.parametrize(
    "command",
    [
        r"\part{Part}",
        r"\chapter{Chapter}",
        r"\section{Section}",
        r"\subsection{Subsection}",
        r"\subsubsection{Subsubsection}",
        r"\paragraph{Paragraph}",
        r"\subparagraph{Subparagraph}",
        r"\section*{Unnumbered}",
        r"\section[Short title]{Long title}",
    ],
    ids=[
        "part",
        "chapter",
        "section",
        "subsection",
        "subsubsection",
        "paragraph",
        "subparagraph",
        "starred",
        "optional-title",
    ],
)
def test_sectioning_commands_are_followed_by_a_blank_line(command: str) -> None:
    """Every standard sectioning command receives one blank source line."""
    assert transform_text(f"  {command}\n  Body.") == f"{command}\n\nBody."


def test_section_comment_stays_attached_before_the_blank_line() -> None:
    """A heading's trailing comment remains on its line before the blank line."""
    source = "\\section{Title} % heading note\nBody."

    assert transform_text(source) == "\\section{Title} % heading note\n\nBody."


def test_existing_section_blank_line_is_not_duplicated() -> None:
    """An existing blank line after a heading remains exactly one blank line."""
    source = "\\subsection{Title}\n\nBody."

    assert transform_text(source) == source
    assert transform_text(transform_text(source)) == source


def test_section_blank_line_uses_the_source_crlf_convention() -> None:
    """Inserted heading separation follows the source's CRLF convention."""
    source = "\\section{Title}\r\nBody."

    assert transform_text(source) == "\\section{Title}\r\n\r\nBody."


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            r"Before \begin{theorem}Body.\end{theorem}",
            "Before\n\\begin{theorem}\nBody.\\end{theorem}",
        ),
        (
            r"\begin{theorem}[Optional title]Body.\end{theorem}",
            "\\begin{theorem}[Optional title]\nBody.\\end{theorem}",
        ),
        (
            r"\begin{itemize}\item One.\end{itemize}",
            "\\begin{itemize}\n\\item One.\\end{itemize}",
        ),
        (
            r"\begin{table}\begin{tabular}{c}Cell\end{tabular}\end{table}",
            (
                "\\begin{table}\n\\begin{tabular}{c}\n"
                "Cell\\end{tabular}\\end{table}"
            ),
        ),
    ],
    ids=[
        "surrounding-prose",
        "optional-title",
        "standard-environment",
        "nested-table-environment",
    ],
)
def test_every_environment_opener_is_on_its_own_line(
    source: str, expected: str
) -> None:
    """A begin command and its optional title occupy an isolated source line."""
    assert transform_text(source) == expected


def test_environment_label_moves_to_the_following_line() -> None:
    """An immediate environment label follows its opener on the next line."""
    source = (
        r"  \begin{theorem}[Optional title]  \label{thm:sample}Body."
        r"\end{theorem}"
    )

    assert transform_text(source) == (
        "\\begin{theorem}[Optional title]\n"
        "\\label{thm:sample}\nBody.\\end{theorem}"
    )


def test_complete_documents_preserve_the_preamble() -> None:
    """Regularization is limited to document bodies in complete documents."""
    source = (
        "  \\newcommand{\\wrapped}{$a=\n b$}\n"
        "\\begin{document}\n  Body.\n\\end{document}"
    )

    assert transform_text(source) == (
        "  \\newcommand{\\wrapped}{$a=\n b$}\n"
        "\\begin{document}\nBody.\n\\end{document}"
    )


def test_regularization_is_idempotent() -> None:
    """A second regularization pass produces byte-identical source."""
    once = transform_text(
        "  Text $a=\n b$. \\begin{equation}x=1\\end{equation} done."
    )

    assert transform_text(once) == once
