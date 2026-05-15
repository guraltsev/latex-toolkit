#!/usr/bin/env python3
"""CLI alias for running ``aligned2baea --reverse``."""

from __future__ import annotations

from latex_toolkit.commands.aligned2baea import main as aligned2baea_command
from latex_toolkit.lib.backup import backup_file  # Imported to keep mutating-command policy explicit.
from latex_toolkit.lib.logging_config import run_command

# This alias overwrites source files through the delegated aligned2baea command.
OVERWRITES_SOURCE_TEX = True


def build_parser():
    """Build the command-line argument parser.

    Returns
    -------
    argparse.ArgumentParser
        Parser configured for the reverse aligned-block conversion alias.
    """

    return aligned2baea_command.build_parser(
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

    return aligned2baea_command.transform_text(text, reverse=True)


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
        return aligned2baea_command.main(
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
