from __future__ import annotations

from pathlib import Path
from unittest import TestCase
import ast
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import lt_cli  # noqa: E402


def _command_entrypoint(command_name: str) -> Path:
    return ROOT / "src" / "commands" / command_name / "main.py"


def _imports_backup_file(command_name: str) -> bool:
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
    module = lt_cli._load_command_module(command_name)
    parser = module.build_parser()
    option_strings: set[str] = set()
    for action in parser._actions:
        option_strings.update(action.option_strings)
    return option_strings


class WritePolicyTests(TestCase):
    def test_read_only_commands_opt_out_explicitly(self) -> None:
        module = lt_cli._load_command_module("list-graphics")
        self.assertIs(getattr(module, "OVERWRITES_SOURCE_TEX", True), False)

    def test_mutating_commands_follow_shared_write_policy(self) -> None:
        for command_name in lt_cli.available_commands():
            module = lt_cli._load_command_module(command_name)
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
                self.assertNotIn("--in-place", option_strings)
