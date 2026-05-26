"""Tests for observable latex_format text-pipeline behavior.

The tests exercise the public ``transform_text`` entrypoint while mocking the
command-level formatter boundaries. Snapper internals, delimiter parsing
details, and exact subprocess invocation mechanics are out of scope.
"""

from __future__ import annotations

from unittest import TestCase
from unittest.mock import patch
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from latex_toolkit.commands.latex_format.main import transform_text  # noqa: E402


class LatexFormatTransformTests(TestCase):
    def test_transform_text_runs_normalization_then_formatting(self) -> None:
        """Latex format normalizes math syntax before the formatter stages."""

        with (
            patch(
                "latex_toolkit.commands.brace_unary_macros.main.transform_text",
                return_value="braced\n",
            ) as brace,
            patch(
                "latex_toolkit.commands.dollar2bracket.main.transform_text",
                return_value="dollar\n",
            ) as dollar,
            patch(
                "latex_toolkit.commands.latex_indent.main.transform_text",
                return_value="indented\n",
            ) as indent,
            patch(
                "latex_toolkit.commands.snapper_format.main.transform_text",
                return_value="snapped\n",
            ) as snapper,
            patch(
                "latex_toolkit.commands.uni2tex.main.transform_text",
                return_value="unicode\n",
            ) as unicode,
        ):
            converted = transform_text("raw\n")

        dollar.assert_called_once_with("raw\n")
        unicode.assert_called_once_with("dollar\n")
        brace.assert_called_once_with("unicode\n")
        snapper.assert_called_once_with("braced\n", max_width=0)
        indent.assert_called_once_with("snapped\n")
        self.assertEqual(converted, "indented\n")

    def test_transform_text_passes_requested_sentence_width_to_snapper(self) -> None:
        """Latex format forwards the max-width option to snapper formatting."""

        with (
            patch(
                "latex_toolkit.commands.brace_unary_macros.main.transform_text",
                return_value="braced\n",
            ),
            patch(
                "latex_toolkit.commands.dollar2bracket.main.transform_text",
                return_value="dollar\n",
            ),
            patch(
                "latex_toolkit.commands.latex_indent.main.transform_text",
                return_value="indented\n",
            ) as indent,
            patch(
                "latex_toolkit.commands.snapper_format.main.transform_text",
                return_value="snapped\n",
            ) as snapper,
            patch(
                "latex_toolkit.commands.uni2tex.main.transform_text",
                return_value="unicode\n",
            ),
        ):
            converted = transform_text("raw\n", max_width=88)

        snapper.assert_called_once_with("braced\n", max_width=88)
        indent.assert_called_once_with("snapped\n")
        self.assertEqual(converted, "indented\n")
