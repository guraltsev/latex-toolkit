r"""Protect standard-input to standard-output command behavior.

The tests invoke each real public command entry point with in-memory standard
streams. Files and the system clipboard remain outside the selected mode, and
the transformation dependencies are real.
"""

import sys
from collections.abc import Callable
from io import StringIO

import pytest

from latex_toolkit.dollar_math_to_latex_delimiters import (
    dollar_math_to_latex_delimiters,
)
from latex_toolkit.full_normalize import full_normalize
from latex_toolkit.latex_delimiters_to_dollar_math import (
    latex_delimiters_to_dollar_math,
)
from latex_toolkit.latex_argument_bracer import latex_argument_bracer
from latex_toolkit.latex_transformer_template import latex_transformer_template
from latex_toolkit.sentence_per_line_transformer import sentence_per_line_transformer
from latex_toolkit.syntax_regularizer import syntax_regularizer


@pytest.mark.parametrize(
    ("main", "source", "expected"),
    [
        pytest.param(
            dollar_math_to_latex_delimiters.main,
            "Inline $x$.",
            r"Inline \(x\).",
            id="dollar-math-to-latex-delimiters",
        ),
        pytest.param(
            latex_delimiters_to_dollar_math.main,
            r"Inline \(x\).",
            "Inline $x$.",
            id="latex-delimiters-to-dollar-math",
        ),
        pytest.param(
            syntax_regularizer.main,
            "$1 +\n 1 = 2$",
            "$1 +1 = 2$",
            id="syntax-regularizer",
        ),
        pytest.param(
            sentence_per_line_transformer.main,
            "First sentence. Second sentence.",
            "First sentence.\nSecond sentence.",
            id="sentence-per-line-transformer",
        ),
        pytest.param(
            full_normalize.main,
            "  First sentence. Second sentence.",
            "First sentence.\nSecond sentence.",
            id="full-normalize",
        ),
        pytest.param(
            latex_transformer_template.main,
            r"\begin{document}\emph{sample}\end{document}",
            r"\begin{document}\textbf{sample}\end{document}",
            id="latex-transformer-template",
        ),
        pytest.param(
            latex_argument_bracer.main,
            r"$\frac12 + x_1$",
            r"$\frac{1}{2} + x_{1}$",
            id="latex-argument-bracer",
        ),
    ],
)
def test_stdin_mode_writes_only_transformed_text_to_stdout(
    main: Callable[[list[str]], int],
    source: str,
    expected: str,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Each command transforms all stdin and emits its exact result on stdout."""
    monkeypatch.setattr(sys, "stdin", StringIO(source))

    assert main(["--stdin"]) == 0
    captured = capsys.readouterr()
    assert captured.out == expected
    assert captured.err == ""
