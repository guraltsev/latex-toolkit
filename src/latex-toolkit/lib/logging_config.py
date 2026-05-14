"""Configure stderr logging for LaTeX toolkit commands.

Command modules call ``run_command(...)`` around their user-visible command
body. Expected operational failures are reported as concise error messages and
unexpected programming errors still surface with their normal traceback.
"""

from __future__ import annotations

from collections.abc import Callable
import logging

# These exceptions usually describe user-visible command failures rather than
# programming defects, so the CLI reports them without a traceback.
COMMAND_ERROR_TYPES = (ImportError, OSError, RuntimeError, ValueError)


def configure_command_logging() -> logging.Logger:
    """Configure and return the shared command logger.

    Returns
    -------
    logging.Logger
        Logger that writes command diagnostics to standard error.
    """

    logger = logging.getLogger("latex-toolkit")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        logger.addHandler(handler)

    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger


def run_command(command_name: str, command: Callable[[], int]) -> int:
    """Run a command body and report expected failures through logging.

    Parameters
    ----------
    command_name : str
        Public command name to include in failure messages.
    command : collections.abc.Callable
        Zero-argument callable that performs the command and returns a process
        exit code.

    Returns
    -------
    int
        The command exit code, or ``1`` when an expected operational failure is
        reported.
    """

    logger = configure_command_logging()
    try:
        return command()
    except COMMAND_ERROR_TYPES as exc:
        logger.error("%s failed: %s", command_name, exc)
        return 1


def run_clipboard_transform(command_name: str, transform: Callable[[str], str]) -> None:
    """Transform clipboard text and log whether the command changed it.

    Parameters
    ----------
    command_name : str
        Public command name to include in status messages.
    transform : collections.abc.Callable
        Function that accepts clipboard text and returns replacement text.

    Returns
    -------
    None
        The system clipboard is replaced with the transformed text.
    """

    from lib.clipboard import read_clipboard_text, write_clipboard_text

    logger = configure_command_logging()

    # Read, transform, and write through the shared clipboard helpers so every
    # command reports the same success and no-op diagnostics.
    original = read_clipboard_text()
    transformed = transform(original)
    if transformed == original:
        logger.info("%s made no clipboard changes.", command_name)
        return

    write_clipboard_text(transformed)
    logger.info(
        "%s updated clipboard (%s -> %s characters).",
        command_name,
        len(original),
        len(transformed),
    )
