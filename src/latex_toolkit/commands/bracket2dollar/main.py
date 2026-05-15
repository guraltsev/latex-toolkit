#!/usr/bin/env python3
"""CLI alias for running ``dollar2bracket --reverse``."""

from __future__ import annotations

from latex_toolkit.commands.dollar2bracket import main as dollar2bracket_command
from latex_toolkit.lib.logging_config import run_command


def build_parser():
    """Build the command-line argument parser.

    Returns
    -------
    argparse.ArgumentParser
        Parser configured for the reverse delimiter conversion alias.
    """

    return dollar2bracket_command.build_parser(
        prog="bracket2dollar",
        description=(
            "Rewrite \\(...\\) and \\[...\\] math delimiters back to $...$ and $$...$$. "
            "By default the input file is overwritten; use -o/--output to write elsewhere."
        ),
        include_reverse=False,
    )


def transform_text(text: str) -> str:
    """Rewrite bracket math delimiters in ``text`` as dollar delimiters.

    Parameters
    ----------
    text : str
        LaTeX source text to transform.

    Returns
    -------
    str
        Source text with matched bracket delimiters rewritten.
    """

    return dollar2bracket_command.transform_text(text, reverse=True)


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
        return dollar2bracket_command.main(
            argv,
            prog="bracket2dollar",
            description=(
                "Rewrite \\(...\\) and \\[...\\] math delimiters back to $...$ and $$...$$. "
                "By default the input file is overwritten; use -o/--output to write elsewhere."
            ),
            include_reverse=False,
            force_reverse=True,
        )

    return run_command("bracket2dollar", run)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
