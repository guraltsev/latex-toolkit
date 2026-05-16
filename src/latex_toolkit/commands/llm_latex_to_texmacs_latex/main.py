#!/usr/bin/env python3
"""Clipboard pipeline for converting LLM-friendly LaTeX back to TeXmacs LaTeX."""

from __future__ import annotations

import argparse

from latex_toolkit.commands.brace_unary_macros import main as brace_unary_macros_command
from latex_toolkit.commands.brace_unary_macros.transform import load_macro_commands
from latex_toolkit.commands.proof2proofstar import main as proof2proofstar_command
from latex_toolkit.commands.texmacs_vert_delimiters import main as texmacs_vert_delimiters_command
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
        prog="llm_latex_to_texmacs_latex",
        description=(
            "Run the LLM-friendly LaTeX clipboard pipeline: brace_unary_macros, "
            "texmacs_vert_delimiters, then proof2proofstar."
        ),
    )
    parser.add_argument(
        "macros_file",
        nargs="?",
        metavar="ABSOLUTE_TOML_PATH",
        help="Compatibility spelling for --macros-file.",
    )
    parser.add_argument(
        "--macros-file",
        dest="macros_file_option",
        metavar="ABSOLUTE_TOML_PATH",
        help="Absolute TOML path whose commands array replaces the default unary macro list.",
    )
    return parser


def pipeline_steps(macros_file: str | None = None) -> tuple[ClipboardPipelineStep, ...]:
    """Return the configured LLM-to-TeXmacs clipboard pipeline steps.

    Parameters
    ----------
    macros_file : str or None
        Optional absolute TOML path used to configure the unary macro bracing
        step.

    Returns
    -------
    tuple of tuple
        Ordered ``(step_name, transform)`` pairs for the clipboard pipeline.

    Raises
    ------
    ValueError
        The macro command TOML path or contents are invalid.
    """

    # Load macro configuration before reading the clipboard so invalid command
    # files fail without changing user clipboard contents.
    commands = load_macro_commands(macros_file) if macros_file else None

    def brace_unary_macros(text: str) -> str:
        return brace_unary_macros_command.transform_text(text, commands=commands)

    return (
        ("brace_unary_macros", brace_unary_macros),
        ("texmacs_vert_delimiters", texmacs_vert_delimiters_command.transform_text),
        ("proof2proofstar", proof2proofstar_command.transform_text),
    )


def transform_text(text: str, *, macros_file: str | None = None) -> str:
    """Run the LLM-to-TeXmacs text pipeline on ``text``.

    Parameters
    ----------
    text : str
        Clipboard text to transform.
    macros_file : str or None
        Optional absolute TOML path used to configure unary macro bracing.

    Returns
    -------
    str
        Text after every pipeline transform has run in order.

    Raises
    ------
    ValueError
        The macro command TOML path or contents are invalid.
    """

    # Share step construction with the CLI so direct Python callers get the
    # same validation and ordered transforms.
    transformed = text
    for _, transform in pipeline_steps(macros_file):
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
        if args.macros_file and args.macros_file_option:
            parser.error("Use either --macros-file or the positional macros file path, not both.")

        macros_file = args.macros_file_option or args.macros_file
        run_clipboard_pipeline("llm_latex_to_texmacs_latex", pipeline_steps(macros_file))
        return 0

    return run_command("llm_latex_to_texmacs_latex", run)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
