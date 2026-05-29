"""Tests for observable snapper_format wrapper behavior around snapper output.

The tests cover the public ``transform_text`` entrypoint while mocking the
external snapper executable. Snapper's own sentence-splitting behavior and
installation flow are out of scope here.
"""

from __future__ import annotations

from pathlib import Path
from unittest import TestCase
from unittest.mock import patch
import subprocess

import test_support  # noqa: F401

from latex_toolkit.commands.snapper_format.main import transform_text  # noqa: E402


class SnapperFormatTransformTests(TestCase):
    def test_transform_text_restores_trailing_blank_lines_for_wrapped_snippets(self) -> None:
        """Wrapped snippets preserve their original trailing blank lines after unwrapping."""

        completed = subprocess.CompletedProcess(
            args=["snapper"],
            returncode=0,
            stdout=(
                "\\begin{document}\n"
                "\\begin{remark} Text.\n"
                "\\end{remark}\n"
                "\\end{document}\n"
            ),
            stderr="",
        )

        with (
            patch(
                "latex_toolkit.commands.snapper_format.main.ensure_snapper",
                return_value=Path("snapper"),
            ),
            patch(
                "latex_toolkit.commands.snapper_format.main.subprocess.run",
                return_value=completed,
            ),
        ):
            result = transform_text("\\begin{remark}\nText.\n\\end{remark}\n\n")

        self.assertEqual(result, "\\begin{remark} Text.\n\\end{remark}\n\n")
