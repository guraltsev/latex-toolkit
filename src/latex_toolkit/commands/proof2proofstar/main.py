#!/usr/bin/env python3
"""CLI alias for running ``proofstar2proof --reverse``."""

from __future__ import annotations

from latex_toolkit.commands.proofstar2proof import main as proofstar2proof_command
from latex_toolkit.lib.backup import backup_file  # Imported to keep mutating-command policy explicit.
from latex_toolkit.lib.logging_config import run_command

# This alias overwrites source files through the delegated proofstar2proof command.
OVERWRITES_SOURCE_TEX = True


def build_parser():
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
