"""Thin dispatcher for lt-cli.

The dispatcher is intentionally narrow: it only selects a command directory and
forwards the remaining argv to that command's own ``main()`` implementation.
"""

from __future__ import annotations

from pathlib import Path
import importlib.util
import sys

SRC_ROOT = Path(__file__).resolve().parent
COMMANDS_ROOT = SRC_ROOT / "commands"


def _ensure_src_on_path() -> None:
    src_text = str(SRC_ROOT)
    if src_text not in sys.path:
        sys.path.insert(0, src_text)


_ensure_src_on_path()


def available_commands() -> list[str]:
    command_names: list[str] = []
    for entry in COMMANDS_ROOT.iterdir():
        if not entry.is_dir():
            continue
        if entry.name.startswith("__"):
            continue
        if (entry / "main.py").exists():
            command_names.append(entry.name)
    return sorted(command_names)


def _load_command_module(command_name: str):
    command_entry = COMMANDS_ROOT / command_name / "main.py"
    if not command_entry.exists():
        raise FileNotFoundError(command_entry)

    module_name = f"lt_cli_command_{command_name.replace('-', '_')}"
    spec = importlib.util.spec_from_file_location(module_name, command_entry)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load command entrypoint: {command_entry}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _usage() -> str:
    commands = available_commands()
    rendered = "\n  ".join(commands) if commands else "<none>"
    return (
        "Usage: lt-cli <command> [command arguments...]\n\n"
        f"Available commands:\n  {rendered}\n"
    )


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)

    if not args or args[0] in {"-h", "--help"}:
        print(_usage(), end="")
        return 0

    command_name = args[0]
    command_argv = args[1:]

    if command_name not in available_commands():
        print(f"Unknown command: {command_name}\n", file=sys.stderr)
        print(_usage(), file=sys.stderr, end="")
        return 2

    module = _load_command_module(command_name)
    if not hasattr(module, "main"):
        print(f"Command {command_name} does not expose main(argv).", file=sys.stderr)
        return 2

    result = module.main(command_argv)
    if isinstance(result, int):
        return result
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
