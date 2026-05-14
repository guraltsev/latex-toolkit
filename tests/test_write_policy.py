"""Tests for shared command-line write policy across public commands.

The tests inspect real command parsers and command entrypoint source files.
They do not assert internal call graphs beyond the public backup import that
marks a command as participating in the shared overwrite policy.
"""

from __future__ import annotations

from pathlib import Path
from unittest import TestCase
import ast
import importlib
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
COMMANDS_ROOT = SRC / "latex-toolkit" / "commands"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def _available_commands() -> tuple[str, ...]:
    """Return command names that expose a ``python -m`` package entrypoint."""

    command_names = [
        entry.name
        for entry in COMMANDS_ROOT.iterdir()
        if entry.is_dir() and (entry / "__main__.py").is_file()
    ]
    return tuple(sorted(command_names))


def _load_command_module(command_name: str) -> object:
    """Import a command implementation module for parser inspection."""

    return importlib.import_module(f"latex-toolkit.commands.{command_name}.main")


def _command_entrypoint(command_name: str) -> Path:
    """Return the source path for a command entrypoint under test."""

    return COMMANDS_ROOT / command_name / "main.py"


def _imports_backup_file(command_name: str) -> bool:
    """Return whether a command entrypoint imports the shared backup helper."""

    tree = ast.parse(_command_entrypoint(command_name).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom):
            continue
        if node.module != "lib.backup":
            continue
        if any(alias.name == "backup_file" for alias in node.names):
            return True
    return False


def _parser_option_strings(command_name: str) -> set[str]:
    """Return all public option strings exposed by a command parser."""

    module = _load_command_module(command_name)
    parser = module.build_parser()
    option_strings: set[str] = set()
    for action in parser._actions:
        option_strings.update(action.option_strings)
    return option_strings


class WritePolicyTests(TestCase):
    def test_package_metadata_does_not_expose_shared_dispatcher(self) -> None:
        """Package metadata does not install a shared command dispatcher."""

        pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

        self.assertNotIn("scripts", pyproject["project"])
        self.assertNotIn("py-modules", pyproject["tool"]["setuptools"])
        self.assertFalse((SRC / "lt_cli.py").exists())

    def test_read_only_commands_opt_out_explicitly(self) -> None:
        """Read-only commands declare that they do not overwrite source TeX."""

        module = _load_command_module("list-graphics")
        self.assertIs(getattr(module, "OVERWRITES_SOURCE_TEX", True), False)

    def test_commands_expose_clipboard_mode(self) -> None:
        """Every public command exposes the README-documented clipboard mode."""

        for command_name in _available_commands():
            with self.subTest(command=command_name):
                option_strings = _parser_option_strings(command_name)
                self.assertIn("--clipboard", option_strings)

    def test_commands_expose_text_transform_function(self) -> None:
        """Every public command exposes a callable text transform function."""

        for command_name in _available_commands():
            with self.subTest(command=command_name):
                module = _load_command_module(command_name)
                self.assertTrue(callable(getattr(module, "transform_text", None)))

    def test_mutating_commands_follow_shared_write_policy(self) -> None:
        """Mutating commands expose backup and output controls consistently."""

        for command_name in _available_commands():
            module = _load_command_module(command_name)
            if getattr(module, "OVERWRITES_SOURCE_TEX", True) is False:
                continue

            with self.subTest(command=command_name):
                self.assertTrue(
                    _imports_backup_file(command_name),
                    f"{command_name} must import backup_file from lib.backup",
                )
                option_strings = _parser_option_strings(command_name)
                self.assertIn("-B", option_strings)
                self.assertIn("--no-backup", option_strings)
                self.assertIn("-o", option_strings)
                self.assertIn("--output", option_strings)
                self.assertIn("--output-file", option_strings)
                self.assertNotIn("--in-place", option_strings)
