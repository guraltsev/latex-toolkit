#!/usr/bin/env python3
"""CLI alias for running ``eqn-star2dmath --reverse``."""

from __future__ import annotations

from latex_toolkit.commands.eqn_star2dmath import main as eqn_star2dmath_command
from latex_toolkit.lib.backup import backup_file  # Imported to keep mutating-command policy explicit.
from latex_toolkit.lib.logging_config import run_command

# This alias overwrites source files through the delegated eqn-star2dmath command.
OVERWRITES_SOURCE_TEX = True


def build_parser():
    """Build the command-line argument parser.

    Returns
    -------
    argparse.ArgumentParser
        Parser configured for the reverse display-math conversion alias.
    """

    return eqn_star2dmath_command.build_parser(
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

    return eqn_star2dmath_command.transform_text(text, reverse=True)


def main(argv: list[str] | None = None) -> int:
    """Run the command-line workflow.

    Parameters
    ----------
    argv : list of str or None
        Command-line arguments to parse. ``None`` reads arguments from
        ``sys.argv``.

    Returns
    -------
    int
        Process exit status, with ``0`` for success and ``1`` for expected
        operational failures.

    Raises
    ------
    SystemExit
        Command-line arguments are invalid.
    """

    def run() -> int:
        return eqn_star2dmath_command.main(
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
