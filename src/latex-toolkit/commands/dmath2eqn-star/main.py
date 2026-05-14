#!/usr/bin/env python3
"""CLI alias for running ``eqn-star2dmath --reverse``."""

from __future__ import annotations

from pathlib import Path
import importlib.util

from lib.backup import backup_file  # Imported to keep mutating-command policy explicit.
from lib.logging_config import run_command

# This alias overwrites source files through the delegated eqn-star2dmath command.
OVERWRITES_SOURCE_TEX = True


def _load_eqn_star2dmath_module():
    command_entry = Path(__file__).resolve().parents[1] / "eqn-star2dmath" / "main.py"
    spec = importlib.util.spec_from_file_location("latex_toolkit_command_eqn_star2dmath_alias", command_entry)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load command entrypoint: {command_entry}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_parser():
    module = _load_eqn_star2dmath_module()
    return module.build_parser(
        prog="dmath2eqn-star",
        description=(
            "Rewrite plain \\[ ... \\] blocks as equation* environments. "
            "By default the input file is overwritten; use -o/--output to write elsewhere."
        ),
        include_reverse=False,
    )


def transform_text(text: str) -> str:
    """Rewrite plain display math in ``text`` as ``equation*`` environments.

    Parameters
    ----------
    text : str
        LaTeX source text to transform.

    Returns
    -------
    str
        Source text with plain display math rewritten as ``equation*``.
    """

    module = _load_eqn_star2dmath_module()
    return module.transform_text(text, reverse=True)


def main(argv: list[str] | None = None) -> int:
    def run() -> int:
        module = _load_eqn_star2dmath_module()
        return module.main(
            argv,
            prog="dmath2eqn-star",
            description=(
                "Rewrite plain \\[ ... \\] blocks as equation* environments. "
                "By default the input file is overwritten; use -o/--output to write elsewhere."
            ),
            include_reverse=False,
            force_reverse=True,
        )

    return run_command("dmath2eqn-star", run)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
