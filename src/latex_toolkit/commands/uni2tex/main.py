#!/usr/bin/env python3
"""CLI alias for running ``tex2uni --reverse``."""

from __future__ import annotations

from latex_toolkit.commands.tex2uni import main as tex2uni_command
from latex_toolkit.lib.backup import backup_file  # Imported to keep mutating-command policy explicit.
from latex_toolkit.lib.logging_config import run_command

# This alias overwrites source files through the delegated tex2uni command.
OVERWRITES_SOURCE_TEX = True


def build_parser():
    """Build the command-line argument parser.

    Returns
    -------
    argparse.ArgumentParser
        Parser configured for the reverse math-symbol conversion alias.
    """

    return tex2uni_command.build_parser(
        prog="uni2tex",
        description=(
            "Convert mapped Unicode math symbols to LaTeX macros in math mode. "
            "By default the input file is overwritten; use -o/--output to write elsewhere."
        ),
        include_reverse=False,
    )


def transform_text(text: str) -> str:
    """Convert mapped Unicode math symbols in ``text`` to LaTeX macros.

    Parameters
    ----------
    text : str
        LaTeX source text to transform.

    Returns
    -------
    str
        Source text with mapped Unicode symbols converted to LaTeX macros.
    """

    return tex2uni_command.transform_text(text, reverse=True)


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
        return tex2uni_command.main(
            argv,
            prog="uni2tex",
            description=(
                "Convert mapped Unicode math symbols to LaTeX macros in math mode. "
                "By default the input file is overwritten; use -o/--output to write elsewhere."
            ),
            include_reverse=False,
            force_reverse=True,
        )

    return run_command("uni2tex", run)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
