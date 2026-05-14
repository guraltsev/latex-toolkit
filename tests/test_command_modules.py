"""Tests for running command packages through ``python -m``.

The tests invoke real command packages in subprocesses with ``src`` on
``PYTHONPATH`` to mirror source-checkout usage. Individual transformation
behavior is covered by feature-specific command tests.
"""

from __future__ import annotations

from pathlib import Path
from unittest import TestCase
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
COMMANDS_ROOT = SRC / "latex-toolkit" / "commands"


def _available_commands() -> tuple[str, ...]:
    """Return command names that expose a package entrypoint."""

    command_names = [
        entry.name
        for entry in COMMANDS_ROOT.iterdir()
        if entry.is_dir() and (entry / "__main__.py").is_file()
    ]
    return tuple(sorted(command_names))


def _pythonpath_env() -> dict[str, str]:
    """Return an environment that imports package modules from ``src``."""

    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC)
    return env


class CommandModuleInvocationTests(TestCase):
    def test_help_is_available_for_each_command_package(self) -> None:
        """Every public command runs through its package without ``.main``."""

        for command_name in _available_commands():
            with self.subTest(command=command_name):
                result = subprocess.run(
                    [sys.executable, "-m", f"latex-toolkit.commands.{command_name}", "--help"],
                    env=_pythonpath_env(),
                    text=True,
                    capture_output=True,
                    check=False,
                )

                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(command_name, result.stdout)

    def test_direct_command_alias_omits_commands_segment(self) -> None:
        """A command can run directly under the root package name."""

        result = subprocess.run(
            [sys.executable, "-m", "latex-toolkit.strip-comments", "--help"],
            env=_pythonpath_env(),
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("strip-comments", result.stdout)

    def test_missing_file_argument_exits_nonzero(self) -> None:
        """A file-oriented command reports a parser error when no input is given."""

        result = subprocess.run(
            [sys.executable, "-m", "latex-toolkit.commands.strip-comments"],
            env=_pythonpath_env(),
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("input", result.stderr)
