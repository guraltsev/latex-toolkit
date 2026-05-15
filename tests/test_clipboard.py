"""Tests for public clipboard helper behavior.

The tests mock the external ``pyperclip`` boundary and do not touch the real
system clipboard. Command integration and platform clipboard manager behavior
are out of scope.
"""

from __future__ import annotations

from pathlib import Path
from unittest import TestCase
from unittest.mock import patch
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from latex_toolkit.lib.clipboard import read_clipboard_text, write_clipboard_text  # noqa: E402


class ClipboardTests(TestCase):
    def test_read_clipboard_uses_pyperclip_text(self) -> None:
        """Reading clipboard text returns the text supplied by pyperclip."""

        with patch("latex_toolkit.lib.clipboard.pyperclip.paste", return_value="alpha"):
            self.assertEqual(read_clipboard_text(), "alpha")

    def test_write_clipboard_uses_pyperclip_text(self) -> None:
        """Writing clipboard text passes the exact text to pyperclip."""

        with patch("latex_toolkit.lib.clipboard.pyperclip.copy") as copy:
            write_clipboard_text("beta")

        copy.assert_called_once_with("beta")
