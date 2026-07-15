r"""Protect public sentence-per-line text, file, and clipboard behavior.

The successful transformation tests use the real pylatexenc parser and pinned
Snapper formatter. Only filesystem destinations, the system clipboard, and
explicit subprocess-failure behavior are mocked or isolated. Parser helper
organization and placeholder representation are outside this module's scope.
"""

from pathlib import Path
from types import SimpleNamespace

import pytest

from sentence_per_line_transformer import process_file, transform_text
from sentence_per_line_transformer import sentence_per_line_transformer as command


def test_sentences_and_paragraphs_use_independent_physical_lines() -> None:
    """Sentences split independently without changing blank-line separators."""
    source = (
        "First sentence. Second sentence.\n\n"
        "Another paragraph. Its next sentence."
    )

    assert transform_text(source) == (
        "First sentence.\nSecond sentence.\n\n"
        "Another paragraph.\nIts next sentence."
    )


def test_transformation_is_idempotent() -> None:
    """A second complete formatting pass produces byte-identical source."""
    once = transform_text(
        r"Text with a \footnote{First note. Second note.} Next sentence."
    )

    assert transform_text(once) == once


def test_comments_and_their_terminating_newlines_are_unchanged() -> None:
    """Comments stay in their sentences while only a real boundary space changes."""
    source = (
        "This is the beginning %comment1\n"
        "of a sentence. Now the next one starts %comment2\n"
        "and ends."
    )

    assert transform_text(source) == (
        "This is the beginning %comment1\n"
        "of a sentence.\n"
        "Now the next one starts %comment2\n"
        "and ends."
    )


def test_captions_and_footnotes_format_depth_first() -> None:
    """Nested prose splits before its invocation is isolated in parent prose."""
    source = (
        r"\caption{First sentence. Second sentence.}"
        "\n"
        r"Text with a \footnote{First note sentence. Second note sentence.} "
        "Next sentence."
    )

    assert transform_text(source) == (
        "\\caption{First sentence.\nSecond sentence.}\n"
        "Text with a\n"
        "\\footnote{First note sentence.\nSecond note sentence.}\n"
        "Next sentence."
    )


def test_attached_footnote_edges_suppress_new_tex_spaces() -> None:
    """Footnote line isolation uses comments where either edge was attached."""
    source = r"Text\footnote{One sentence. Two sentences.}, then ends. Next."

    transformed = transform_text(source)

    assert transformed == (
        "Text%\n"
        "\\footnote{One sentence.\nTwo sentences.}%\n"
        ", then ends.\nNext."
    )
    assert transform_text(transformed) == transformed


@pytest.mark.parametrize(
    "source",
    [
        (
            "We obtain the following equation:\n"
            "\\[\n1+1=2,\n\\]\n"
            "where the numbers are defined using Peano's rules."
        ),
        (
            "We obtain the following equation:\n"
            "\\[ 1+1=2, \\]\n"
            "where the numbers are defined using Peano's rules."
        ),
        (
            "We obtain the following equation:  \\[ 1+1=2, \\] "
            "where the numbers are defined using Peano's rules."
        ),
    ],
    ids=["multiline", "own-line-compact", "prose-inline"],
)
def test_display_math_and_adjacent_layout_are_byte_identical(source: str) -> None:
    """Supported display layouts remain byte-for-byte unchanged."""
    assert transform_text(source) == source


def test_formatting_resumes_on_both_sides_of_display_math() -> None:
    """Display source stays fixed while prose on both sides still formats."""
    source = "Before one. Before two.  \\[ x. \\] After one. After two."

    assert transform_text(source) == (
        "Before one.\nBefore two.  \\[ x. \\] After one.\nAfter two."
    )


def test_inline_math_is_unchanged_at_a_sentence_boundary() -> None:
    """Inline math retains exact token text while its following sentence splits."""
    source = r"We know $1 + 1 = 2$. This follows."

    transformed = transform_text(source)

    assert transformed == "We know $1 + 1 = 2$.\nThis follows."
    assert transform_text(transformed) == transformed


def test_inline_math_joins_wrapped_sentence_text() -> None:
    """Inline math follows sentence text on one line while retaining its bytes."""
    source = "Write\n  $u_j = (x_j, t_j)$\n  and conclude. Next sentence."

    assert transform_text(source) == (
        "Write $u_j = (x_j, t_j)$ and conclude.\nNext sentence."
    )


def test_inline_math_joins_crlf_wrapping_without_changing_line_endings() -> None:
    """CRLF beside inline math joins safely and remains the output convention."""
    source = "Write\r\n  $u_j = (x_j, t_j)$\r\n  and conclude. Next sentence."

    assert transform_text(source) == (
        "Write $u_j = (x_j, t_j)$ and conclude.\r\nNext sentence."
    )


def test_verbatim_content_is_opaque_while_neighboring_prose_formats() -> None:
    """Verbatim lines stay exact and ordinary prose after the block still splits."""
    source = (
        "\\begin{verbatim}\nFirst. Second.\n\\end{verbatim}\n"
        "Prose one. Prose two."
    )

    assert transform_text(source) == (
        "\\begin{verbatim}\nFirst. Second.\n\\end{verbatim}\n"
        "Prose one.\nProse two."
    )


def test_complete_documents_preserve_the_preamble_and_wrapper() -> None:
    """Only document body prose changes and no synthetic wrapper leaks."""
    source = (
        "\\newcommand{\\sample}{Preamble. Text.}\n"
        "\\begin{document}Body one. Body two.\\end{document}"
    )

    assert transform_text(source) == (
        "\\newcommand{\\sample}{Preamble. Text.}\n"
        "\\begin{document}Body one.\nBody two.\\end{document}"
    )


def test_crlf_and_exact_trailing_newline_run_are_preserved() -> None:
    """Inserted boundaries use CRLF and trailing CRLF bytes remain unchanged."""
    source = "First sentence. Second sentence.\r\n\r\n\r\n"

    assert transform_text(source) == (
        "First sentence.\r\nSecond sentence.\r\n\r\n\r\n"
    )


@pytest.mark.parametrize(
    "source",
    [
        "First sentence. Second sentence. \\end{itemize}",
        "\\begin{document}First sentence. Second sentence.\\end{itemize}",
    ],
    ids=["unmatched-closing-environment", "mismatched-document-environment"],
)
def test_incomplete_latex_is_preserved_without_formatting(source: str) -> None:
    """Incomplete parser scopes remain byte-identical instead of crashing."""
    assert transform_text(source) == source


def test_proof_fixture_formats_around_display_math_without_losing_wrappers() -> None:
    """A proof with many displays formats fully and retains its environment."""
    fixture_path = Path(__file__).parent / "fixtures" / "proof.tex"
    source = fixture_path.read_text(encoding="utf-8")

    transformed = transform_text(source)

    assert "zero-sum hyperplane.\nWrite" in transformed
    assert "Write $u_j = (x_j, t_j) \\in \\mathbb{R}^d \\times \\mathbb{R}$." in transformed
    assert "proves the claim.\nThe distributional statement" in transformed
    assert transformed.count("\\begin{proof}") == 1
    assert transformed.count("\\end{proof}") == 1
    assert transform_text(transformed) == transformed


def test_process_failure_leaves_existing_destination_unchanged(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A Snapper failure occurs before file output is opened or replaced."""
    source_path = tmp_path / "paper.tex"
    output_path = tmp_path / "sentences.tex"
    source_path.write_text("First. Second.", encoding="utf-8")
    output_path.write_text("existing destination", encoding="utf-8")

    monkeypatch.setattr(
        command.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=3,
            stdout=b"",
            stderr=b"formatter error",
        ),
    )

    with pytest.raises(RuntimeError, match="formatter error"):
        process_file(source_path, output_path)
    assert output_path.read_text(encoding="utf-8") == "existing destination"


def test_clipboard_failure_does_not_replace_clipboard_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Clipboard output is copied only after Snapper completes successfully."""
    copied: list[str] = []
    fake_clipboard = SimpleNamespace(
        paste=lambda: "First. Second.",
        copy=copied.append,
    )
    monkeypatch.setitem(__import__("sys").modules, "pyperclip", fake_clipboard)
    monkeypatch.setattr(
        command.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=4,
            stdout=b"",
            stderr=b"formatter error",
        ),
    )

    with pytest.raises(RuntimeError, match="formatter error"):
        command.main(["--clipboard"])
    assert copied == []
