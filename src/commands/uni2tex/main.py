#!/usr/bin/env python3
"""CLI alias for running ``tex2uni --reverse``."""

from __future__ import annotations

from pathlib import Path
import importlib.util

from lib.backup import backup_file  # Imported to keep mutating-command policy explicit.

OVERWRITES_SOURCE_TEX = True


def _load_tex2uni_module():
    command_entry = Path(__file__).resolve().parents[1] / "tex2uni" / "main.py"
    spec = importlib.util.spec_from_file_location("lt_cli_command_tex2uni_alias", command_entry)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load command entrypoint: {command_entry}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_parser():
    module = _load_tex2uni_module()
    return module.build_parser(
        prog="uni2tex",
        description=(
            "Convert mapped Unicode math symbols to LaTeX macros in math mode. "
            "By default the input file is overwritten; use -o/--output to write elsewhere."
        ),
        include_reverse=False,
    )


def main(argv: list[str] | None = None) -> int:
    module = _load_tex2uni_module()
    return module.main(
        argv,
        prog="uni2tex",
        description=(
            "Convert mapped Unicode math symbols to LaTeX macros in math mode. "
            "By default the input file is overwritten; use -o/--output to write elsewhere."
        ),
        include_reverse=False,
        force_reverse=True,
    )


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
