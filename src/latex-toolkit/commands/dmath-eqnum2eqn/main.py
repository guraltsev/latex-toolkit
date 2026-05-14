#!/usr/bin/env python3
"""CLI alias for running ``eqn2dmath-eqnum --reverse``."""

from __future__ import annotations

from pathlib import Path
import importlib.util

from lib.backup import backup_file  # Imported to keep mutating-command policy explicit.

# This alias overwrites source files through the delegated eqn2dmath-eqnum command.
OVERWRITES_SOURCE_TEX = True


def _load_eqn2dmath_eqnum_module():
    command_entry = Path(__file__).resolve().parents[1] / "eqn2dmath-eqnum" / "main.py"
    spec = importlib.util.spec_from_file_location("latex_toolkit_command_eqn2dmath_eqnum_alias", command_entry)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load command entrypoint: {command_entry}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_parser():
    module = _load_eqn2dmath_eqnum_module()
    return module.build_parser(
        prog="dmath-eqnum2eqn",
        description=(
            "Rewrite \\[\\eqnum ... \\] blocks as equation environments. "
            "By default the input file is overwritten; use -o/--output to write elsewhere."
        ),
        include_reverse=False,
    )


def transform_text(text: str) -> str:
    """Rewrite ``\\[\\eqnum ... \\]`` display math in ``text`` as equations.

    Parameters
    ----------
    text : str
        LaTeX source text to transform.

    Returns
    -------
    str
        Source text with standalone ``\\eqnum`` display math rewritten.
    """

    module = _load_eqn2dmath_eqnum_module()
    return module.transform_text(text, reverse=True)


def main(argv: list[str] | None = None) -> int:
    module = _load_eqn2dmath_eqnum_module()
    return module.main(
        argv,
        prog="dmath-eqnum2eqn",
        description=(
            "Rewrite \\[\\eqnum ... \\] blocks as equation environments. "
            "By default the input file is overwritten; use -o/--output to write elsewhere."
        ),
        include_reverse=False,
        force_reverse=True,
    )


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
