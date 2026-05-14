#!/usr/bin/env python3
"""CLI alias for running ``aligned2baea --reverse``."""

from __future__ import annotations

from pathlib import Path
import importlib.util

from lib.backup import backup_file  # Imported to keep mutating-command policy explicit.
from lib.logging_config import run_command

# This alias overwrites source files through the delegated aligned2baea command.
OVERWRITES_SOURCE_TEX = True


def _load_aligned2baea_module():
    command_entry = Path(__file__).resolve().parents[1] / "aligned2baea" / "main.py"
    spec = importlib.util.spec_from_file_location("latex_toolkit_command_aligned2baea_alias", command_entry)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load command entrypoint: {command_entry}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_parser():
    module = _load_aligned2baea_module()
    return module.build_parser(
        prog="baea2aligned",
        description=(
            "Expand \\ba / \\ea into exact \\begin{aligned}[t] / \\end{aligned} blocks. "
            "By default the input file is overwritten; use -o/--output to write elsewhere."
        ),
        include_reverse=False,
    )


def transform_text(text: str) -> str:
    """Expand ``\\ba`` / ``\\ea`` shorthands in ``text``.

    Parameters
    ----------
    text : str
        LaTeX source text to transform.

    Returns
    -------
    str
        Source text with shorthands expanded to ``aligned`` environments.
    """

    module = _load_aligned2baea_module()
    return module.transform_text(text, reverse=True)


def main(argv: list[str] | None = None) -> int:
    def run() -> int:
        module = _load_aligned2baea_module()
        return module.main(
            argv,
            prog="baea2aligned",
            description=(
                "Expand \\ba / \\ea into exact \\begin{aligned}[t] / \\end{aligned} blocks. "
                "By default the input file is overwritten; use -o/--output to write elsewhere."
            ),
            include_reverse=False,
            force_reverse=True,
        )

    return run_command("baea2aligned", run)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
