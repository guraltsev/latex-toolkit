"""Command transform tests for ``ltae`` to ``aligned[t]`` conversion.

The tests call the command's public text transform and assert observable LaTeX
rewrites. CLI write policy and low-level tokenizer spans are out of scope.
"""

from __future__ import annotations

from pathlib import Path
from unittest import TestCase
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from latex_toolkit.commands.ltae2aligned.main import transform_text  # noqa: E402


class LtaeAlignedTransformTests(TestCase):
    def test_ltae_conversion_prefixes_top_level_rows_only(self) -> None:
        """Ltae conversion adds row markers without entering nested environments."""

        source = (
            "\\documentclass{article}\n"
            "\\newcommand{\\keep}{\\begin{ltae}p\\end{ltae}}\n"
            "\\begin{document}\n"
            "\\begin{ltae}\n"
            "x = 1\\\\\n"
            "\\begin{cases}\n"
            "a, & a > 0\\\\\n"
            "-a, & a < 0\n"
            "\\end{cases}\\\\[0.5em]\n"
            "&z = 3\n"
            "\\end{ltae}\n"
            "% \\begin{ltae}ignored\\end{ltae}\n"
            "\\end{document}\n"
            "\\begin{ltae}tail\\end{ltae}\n"
        )

        converted = transform_text(source)

        self.assertEqual(
            converted,
            "\\documentclass{article}\n"
            "\\newcommand{\\keep}{\\begin{ltae}p\\end{ltae}}\n"
            "\\begin{document}\n"
            "\\begin{aligned}[t]\n"
            "&x = 1\\\\\n"
            "&\\begin{cases}\n"
            "a, & a > 0\\\\\n"
            "-a, & a < 0\n"
            "\\end{cases}\\\\[0.5em]\n"
            "&z = 3\n"
            "\\end{aligned}\n"
            "% \\begin{ltae}ignored\\end{ltae}\n"
            "\\end{document}\n"
            "\\begin{ltae}tail\\end{ltae}\n",
        )

    def test_ltae_conversion_does_not_treat_grouped_linebreaks_as_rows(self) -> None:
        """Grouped linebreaks do not cause top-level row marker insertion."""

        source = "\\begin{ltae}\\text{a\\\\b}\\\\c\\end{ltae}"

        converted = transform_text(source)

        self.assertEqual(converted, "\\begin{aligned}[t]&\\text{a\\\\b}\\\\&c\\end{aligned}")
