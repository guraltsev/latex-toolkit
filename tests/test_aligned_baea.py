"""Command transform tests for aligned-environment shorthand conversion.

The tests call the command's public text transform directly and assert
observable source rewrites. CLI write policy and low-level token spans are out
of scope.
"""

from __future__ import annotations

from pathlib import Path
from unittest import TestCase
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from latex_toolkit.commands.aligned2baea.main import transform_text  # noqa: E402


class AlignedBaeaTransformTests(TestCase):
    def test_forward_conversion_only_compresses_exact_aligned_t_in_document_body(self) -> None:
        """Forward conversion compresses exact document-body aligned[t] blocks only."""

        source = (
            "\\documentclass{article}\n"
            "\\newcommand{\\keep}{\\begin{aligned}[t]p\\end{aligned}}\n"
            "\\begin{document}\n"
            "A \\begin{aligned}[t]x\\end{aligned}alpha B\n"
            "\\begin{aligned}u\\end{aligned}\n"
            "% \\begin{aligned}[t]ignored\\end{aligned}\n"
            "\\end{document}\n"
            "\\begin{aligned}[t]tail\\end{aligned}\n"
        )

        converted = transform_text(source)

        self.assertEqual(
            converted,
            "\\documentclass{article}\n"
            "\\newcommand{\\keep}{\\begin{aligned}[t]p\\end{aligned}}\n"
            "\\begin{document}\n"
            "A \\ba x\\ea alpha B\n"
            "\\begin{aligned}u\\end{aligned}\n"
            "% \\begin{aligned}[t]ignored\\end{aligned}\n"
            "\\end{document}\n"
            "\\begin{aligned}[t]tail\\end{aligned}\n",
        )

    def test_reverse_conversion_respects_control_word_boundaries(self) -> None:
        """Reverse conversion expands shorthand tokens without touching longer names."""

        source = (
            "\\begin{document}\n"
            "\\ba x\\ea alpha\n"
            "\\baalpha \\eaalpha\n"
            "% \\ba ignored\\ea\n"
            "\\end{document}\n"
        )

        converted = transform_text(source, reverse=True)

        self.assertEqual(
            converted,
            "\\begin{document}\n"
            "\\begin{aligned}[t] x\\end{aligned} alpha\n"
            "\\baalpha \\eaalpha\n"
            "% \\ba ignored\\ea\n"
            "\\end{document}\n",
        )
