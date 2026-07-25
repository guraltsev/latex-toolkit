r"""Protect standard-input to standard-output command behavior.

The tests invoke each real public command entry point with in-memory standard
streams. Files and the system clipboard remain outside the selected mode, and
the transformation dependencies are real.
"""

import os
import subprocess
import sys
from collections.abc import Callable
from io import StringIO
from pathlib import Path

import pytest

from latex_toolkit.math_dollar2latex import (
    math_dollar2latex,
)
from latex_toolkit.full_normalize import full_normalize
from latex_toolkit.math_latex2dollar import (
    math_latex2dollar,
)
from latex_toolkit.brace_args import brace_args
from latex_toolkit.greek_latex2unicode import greek_latex2unicode
from latex_toolkit.greek_unicode2latex import greek_unicode2latex
from latex_toolkit.template import template
from latex_toolkit.sentence_per_line import sentence_per_line
from latex_toolkit.syntax_regularizer import syntax_regularizer


@pytest.mark.parametrize(
    ("main", "source", "expected"),
    [
        pytest.param(
            math_dollar2latex.main,
            "Inline $x$.",
            r"Inline \(x\).",
            id="dollar-math-to-latex-delimiters",
        ),
        pytest.param(
            math_latex2dollar.main,
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
            sentence_per_line.main,
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
            template.main,
            r"\begin{document}\emph{sample}\end{document}",
            r"\begin{document}\textbf{sample}\end{document}",
            id="latex-transformer-template",
        ),
        pytest.param(
            brace_args.main,
            r"$\frac12 + x_1$",
            r"$\frac{1}{2} + x_{1}$",
            id="brace-args",
        ),
        pytest.param(
            greek_unicode2latex.main,
            "Text α; $α + Ω$.",
            r"Text α; $\alpha + \Omega$.",
            id="unicode-greek-to-latex",
        ),
        pytest.param(
            greek_latex2unicode.main,
            r"Text \alpha; $\alpha + \Omega$.",
            "Text \\alpha; $α + Ω$.",
            id="latex-greek-to-unicode",
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


def test_greek_latex2unicode_stdin_uses_utf8_despite_windows_code_page() -> None:
    """The Greek reverse CLI emits UTF-8 when the inherited encoding is CP-1252."""
    source_root = Path(__file__).parents[1] / "src"
    environment = os.environ | {
        "PYTHONIOENCODING": "cp1252",
        "PYTHONPATH": str(source_root),
    }

    completed = subprocess.run(
        [
            sys.executable,
            "-X",
            "utf8=0",
            "-m",
            "latex_toolkit.greek_latex2unicode",
            "--stdin",
        ],
        input=b"$\\alpha$",
        capture_output=True,
        check=False,
        env=environment,
    )

    assert completed.returncode == 0, completed.stderr.decode("ascii")
    assert completed.stdout == "$\u03b1$".encode("utf-8")
    assert completed.stderr == b""
