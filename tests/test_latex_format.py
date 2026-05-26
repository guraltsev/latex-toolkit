"""Tests for observable latex_format text-pipeline behavior.

The tests exercise the public ``transform_text`` entrypoint while mocking the
formatter subprocess boundaries. Latexindent internals, snapper implementation
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
    def test_transform_text_returns_latexindent_output(self) -> None:
        """Latex format currently behaves like a pure latexindent transform."""

        with patch(
            "latex_toolkit.commands.latex_indent.main.transform_text",
            return_value="indented\n",
        ) as indent:
            converted = transform_text("raw\n")

        indent.assert_called_once_with("raw\n")
        self.assertEqual(converted, "indented\n")
