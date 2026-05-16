#!/usr/bin/env python3
"""Clipboard pipeline for normalizing TeXmacs snippets."""

from __future__ import annotations

import argparse

from latex_toolkit.commands.tm_alignedt2ltae import main as tm_alignedt2ltae_command
from latex_toolkit.lib.logging_config import (
    ClipboardPipelineStep,
    run_clipboard_pipeline,
    run_command,
)


# The TeXmacs snippet pipeline currently has one step, but keeping it in the
# same Python pipeline form makes future additions testable.
PIPELINE_STEPS: tuple[ClipboardPipelineStep, ...] = (
    ("tm_alignedt2ltae", tm_alignedt2ltae_command.transform_text),
)


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser.

    Returns
    -------
    argparse.ArgumentParser
        Parser configured for the clipboard pipeline command.
    """

    return argparse.ArgumentParser(
        prog="tm2tm",
        description="Run the TeXmacs snippet clipboard normalization pipeline.",
    )


def transform_text(text: str) -> str:
    """Run the TeXmacs snippet text pipeline on ``text``.

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
    for _, transform in PIPELINE_STEPS:
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
        run_clipboard_pipeline("tm2tm", PIPELINE_STEPS)
        return 0

    return run_command("tm2tm", run)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
