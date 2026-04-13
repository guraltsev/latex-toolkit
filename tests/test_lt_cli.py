from __future__ import annotations

from pathlib import Path
from unittest import TestCase
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "src" / "lt_cli.py"


class LtCliTests(TestCase):
    def test_help_lists_available_commands(self) -> None:
        result = subprocess.run(
            [sys.executable, str(CLI), "--help"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("expand-includes", result.stdout)
        self.assertIn("strip-comments", result.stdout)
        self.assertIn("list-graphics", result.stdout)
        self.assertIn("tex2uni", result.stdout)
        self.assertIn("uni2tex", result.stdout)

    def test_unknown_command_exits_nonzero(self) -> None:
        result = subprocess.run(
            [sys.executable, str(CLI), "does-not-exist"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("Unknown command", result.stderr)
