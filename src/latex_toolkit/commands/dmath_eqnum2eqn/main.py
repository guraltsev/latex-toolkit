#!/usr/bin/env python3
"""CLI alias for running ``eqn2dmath-eqnum --reverse``."""

from __future__ import annotations

from latex_toolkit.commands.eqn2dmath_eqnum import main as eqn2dmath_eqnum_command
from latex_toolkit.lib.backup import backup_file  # Imported to keep mutating-command policy explicit.
from latex_toolkit.lib.logging_config import run_command

# This alias overwrites source files through the delegated eqn2dmath-eqnum command.
OVERWRITES_SOURCE_TEX = True


def build_parser():
    return eqn2dmath_eqnum_command.build_parser(
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

    return eqn2dmath_eqnum_command.transform_text(text, reverse=True)


def main(argv: list[str] | None = None) -> int:
    def run() -> int:
        return eqn2dmath_eqnum_command.main(
            argv,
            prog="dmath-eqnum2eqn",
            description=(
                "Rewrite \\[\\eqnum ... \\] blocks as equation environments. "
                "By default the input file is overwritten; use -o/--output to write elsewhere."
            ),
            include_reverse=False,
            force_reverse=True,
        )

    return run_command("dmath-eqnum2eqn", run)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
