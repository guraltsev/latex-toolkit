#!/usr/bin/env python3
"""CLI alias for running ``dollar2bracket --reverse``."""

from __future__ import annotations

from latex_toolkit.commands.dollar2bracket import main as dollar2bracket_command
from latex_toolkit.lib.backup import backup_file  # Imported to keep mutating-command policy explicit.
from latex_toolkit.lib.logging_config import run_command

# This alias overwrites source files through the delegated dollar2bracket command.
OVERWRITES_SOURCE_TEX = True


def build_parser():
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
