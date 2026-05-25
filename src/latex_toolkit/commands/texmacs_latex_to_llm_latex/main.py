#!/usr/bin/env python3
"""Clipboard pipeline for converting TeXmacs-generated LaTeX to LLM-friendly LaTeX."""

from __future__ import annotations

import argparse

from latex_toolkit.commands.dollar2bracket import main as dollar2bracket_command
from latex_toolkit.commands.ltae2aligned import main as ltae2aligned_command
from latex_toolkit.commands.proofstar2proof import main as proofstar2proof_command
from latex_toolkit.commands.tmscript2substack import main as tmscript2substack_command
from latex_toolkit.commands.uni2tex import main as uni2tex_command
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

    return argparse.ArgumentParser(
        prog="texmacs_latex_to_llm_latex",
        description=(
            "Run the TeXmacs-generated LaTeX clipboard pipeline: dollar2bracket, "
            "ltae2aligned, tmscript2substack, proofstar2proof, then uni2tex."
        ),
    )


def pipeline_steps() -> tuple[ClipboardPipelineStep, ...]:
    """Return the configured TeXmacs-to-LLM clipboard pipeline steps.

    Returns
    -------
    tuple of tuple
        Ordered ``(step_name, transform)`` pairs for the clipboard pipeline.
    """

    # The sequence mirrors the historical Windows launcher and is the
    # user-visible order in which clipboard text is normalized.
    return (
        ("dollar2bracket", dollar2bracket_command.transform_text),
        ("ltae2aligned", ltae2aligned_command.transform_text),
        ("tmscript2substack", tmscript2substack_command.transform_text),
        ("proofstar2proof", proofstar2proof_command.transform_text),
        ("uni2tex", uni2tex_command.transform_text),
    )


def transform_text(text: str) -> str:
    """Run the TeXmacs-to-LLM text pipeline on ``text``.

    Parameters
    ----------
    text : str
        Clipboard text to transform.

    Returns
    -------
    str
        Text after every pipeline transform has run in order.
    """

    # Apply the same ordered transforms used by the clipboard command so Python
    # callers can reuse the pipeline without touching the system clipboard.
    transformed = text
    for _, transform in pipeline_steps():
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
        parser.parse_args(argv)
        run_clipboard_pipeline("texmacs_latex_to_llm_latex", pipeline_steps())
        return 0

    return run_command("texmacs_latex_to_llm_latex", run)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
