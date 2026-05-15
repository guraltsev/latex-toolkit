#!/usr/bin/env python3
"""CLI alias for running ``eqn2dmath-eqnum --reverse``."""

from __future__ import annotations

from latex_toolkit.commands.eqn2dmath_eqnum import main as eqn2dmath_eqnum_command
from latex_toolkit.lib.logging_config import run_command


def build_parser():
    """Build the command-line argument parser.

    Returns
    -------
    argparse.ArgumentParser
        Parser configured for the reverse numbered display-math alias.
    """

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
