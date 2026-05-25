#!/usr/bin/env python3
"""Clipboard pipeline for converting TeXmacs-generated LaTeX to ordinary LaTeX."""

from __future__ import annotations

from collections.abc import Iterable
import argparse

from latex_toolkit.commands.delete_macros import main as delete_macros_command
from latex_toolkit.commands.delete_macros.transform import load_delete_macro_commands
from latex_toolkit.commands.texmacs_latex_to_llm_latex.main import (
    pipeline_steps as texmacs_to_llm_pipeline_steps,
)
from latex_toolkit.lib.logging_config import (
    ClipboardPipelineStep,
    run_clipboard_pipeline,
    run_command,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser.

    Returns
    -------
    argparse.ArgumentParser
        Parser configured for the clipboard pipeline command.
    """

    parser = argparse.ArgumentParser(
        prog="texmacs_latex_to_latex",
        description=(
            "Run the TeXmacs-generated LaTeX clipboard pipeline: dollar2bracket, "
            "ltae2aligned, tmscript2substack, proofstar2proof, uni2tex, then "
            "delete_macros."
        ),
    )
    parser.add_argument(
        "--macros-file",
        metavar="ABSOLUTE_TOML_PATH",
        help="Absolute TOML path whose commands array replaces the deleted macro list.",
    )
    return parser


def pipeline_steps(commands: Iterable[str] | None = None) -> tuple[ClipboardPipelineStep, ...]:
    """Return the configured TeXmacs-to-LaTeX clipboard pipeline steps.

    Parameters
    ----------
    commands : collections.abc.Iterable of str, optional
        Deleted macro command names to use instead of the default list.

    Returns
    -------
    tuple of tuple
        Ordered ``(step_name, transform)`` pairs for the clipboard pipeline.
    """

    delete_commands = None if commands is None else tuple(commands)

    def delete_macros(text: str) -> str:
        return delete_macros_command.transform_text(text, commands=delete_commands)

    return (*texmacs_to_llm_pipeline_steps(), ("delete_macros", delete_macros))


def transform_text(text: str, *, commands: Iterable[str] | None = None) -> str:
    """Run the TeXmacs-to-LaTeX text pipeline on ``text``.

    Parameters
    ----------
    text : str
        Clipboard text to transform.
    commands : collections.abc.Iterable of str, optional
        Deleted macro command names to use instead of the default list.

    Returns
    -------
    str
        Text after every pipeline transform has run in order.
    """

    # Share step construction with the CLI so direct Python callers get the
    # same ordered transforms and configurable delete list.
    transformed = text
    for _, transform in pipeline_steps(commands):
        transformed = transform(transformed)
    return transformed


def main(argv: list[str] | None = None) -> int:
    """Run the clipboard pipeline command.

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
        parser = build_parser()
        args = parser.parse_args(argv)
        commands = load_delete_macro_commands(args.macros_file) if args.macros_file else None
        run_clipboard_pipeline("texmacs_latex_to_latex", pipeline_steps(commands))
        return 0

    return run_command("texmacs_latex_to_latex", run)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
