r"""Protect the public text and file transformation behavior.

The tests use the real parser, renderer, and filesystem. Clipboard integration
and the internal visitor organization are outside this module's scope.
"""

from pathlib import Path

from latex_transformer_template import process_file, transform_text


def test_transform_text_changes_only_the_document_body() -> None:
    r"""The example rewrite changes nested body macros but preserves the preamble."""
    source = (
        r"\newcommand{\term}[1]{\emph{#1}}"
        "\n"
        r"\begin{document}\section{An \emph{important} result}\end{document}"
    )

    transformed = transform_text(source)

    assert r"\newcommand{\term}[1]{\emph{#1}}" in transformed
    assert r"\section{An \textbf{important} result}" in transformed


def test_process_file_preserves_the_source_and_writes_the_result(
    tmp_path: Path,
) -> None:
    """File processing leaves its source intact and writes transformed UTF-8 text."""
    source_path = tmp_path / "paper.tex"
    output_path = tmp_path / "paper_modified.tex"
    source = r"\begin{document}Café: \emph{résumé}\end{document}"
    source_path.write_text(source, encoding="utf-8")

    result_path = process_file(source_path, output_path)

    assert result_path == output_path
    assert source_path.read_text(encoding="utf-8") == source
    assert output_path.read_text(encoding="utf-8") == (
        r"\begin{document}Café: \textbf{résumé}\end{document}"
    )
