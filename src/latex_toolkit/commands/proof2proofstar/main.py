#!/usr/bin/env python3
"""CLI alias for running ``proofstar2proof --reverse``."""

from __future__ import annotations

from latex_toolkit.commands.proofstar2proof import main as proofstar2proof_command
from latex_toolkit.lib.logging_config import run_command


def build_parser():
    """Build the command-line argument parser.

    Returns
    -------
    argparse.ArgumentParser
        Parser configured for the reverse proof conversion alias.
    """

    return proofstar2proof_command.build_parser(
        prog="proof2proofstar",
        description=(
            "Rewrite \\begin{proof}[Title] ... \\end{proof} environments back to "
            "\\begin{proof*}{Title} ... \\end{proof*}. By default the input file "
            "is overwritten; use -o/--output to write elsewhere."
        ),
        include_reverse=False,
    )


def transform_text(text: str) -> str:
    """Rewrite titled ``proof`` environments in ``text`` as ``proof*``.

    Parameters
    ----------
    text : str
        LaTeX source text to transform.

    Returns
    -------
    str
        Source text with converted proof environments.
    """

    return proofstar2proof_command.transform_text(text, reverse=True)


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
        return proofstar2proof_command.main(
            argv,
            prog="proof2proofstar",
            description=(
                "Rewrite \\begin{proof}[Title] ... \\end{proof} environments back to "
                "\\begin{proof*}{Title} ... \\end{proof*}. By default the input file "
                "is overwritten; use -o/--output to write elsewhere."
            ),
            include_reverse=False,
            force_reverse=True,
        )

    return run_command("proof2proofstar", run)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
