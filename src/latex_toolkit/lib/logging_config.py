"""Configure stderr logging for LaTeX toolkit commands.

Command modules call ``run_command(...)`` around their user-visible command
body. Expected operational failures are reported as concise error messages and
unexpected programming errors still surface with their normal traceback.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
import logging

# These exceptions usually describe user-visible command failures rather than
# programming defects, so the CLI reports them without a traceback.
COMMAND_ERROR_TYPES = (ImportError, OSError, RuntimeError, ValueError)

# A clipboard pipeline step carries the user-facing step label and the text
# transform that should run at that point in the pipeline.
ClipboardPipelineStep = tuple[str, Callable[[str], str]]


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

    Raises
    ------
    RuntimeError
        Clipboard text cannot be read or written.
    """

    from latex_toolkit.lib.clipboard import read_clipboard_text, write_clipboard_text

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


def run_clipboard_pipeline(command_name: str, steps: Iterable[ClipboardPipelineStep]) -> None:
    """Run ordered text transforms against the system clipboard.

    Each successful step sees the previous step's output. The clipboard is
    updated after every changing step, so a later step failure leaves the same
    observable partial result as running the individual clipboard commands in
    sequence.

    Parameters
    ----------
    command_name : str
        Public pipeline command name to include in status messages.
    steps : collections.abc.Iterable of tuple
        Ordered ``(step_name, transform)`` pairs. Each transform accepts the
        current clipboard text and returns replacement text.

    Returns
    -------
    None
        The system clipboard is updated with each successful changing step.

    Raises
    ------
    RuntimeError
        A configured step fails with an expected command error.
    ValueError
        No pipeline steps were provided.
    """

    from latex_toolkit.lib.clipboard import read_clipboard_text, write_clipboard_text

    logger = configure_command_logging()
    pipeline_steps = tuple(steps)
    if not pipeline_steps:
        raise ValueError(f"{command_name} must define at least one clipboard step.")

    # Keep the pipeline's in-memory value aligned with the clipboard after each
    # successful changing step, matching the old batch-script sequencing.
    current = read_clipboard_text()
    logger.info("%s starting clipboard pipeline.", command_name)
    for step_name, transform in pipeline_steps:
        logger.info("%s running %s.", command_name, step_name)
        try:
            transformed = transform(current)
        except COMMAND_ERROR_TYPES as exc:
            raise RuntimeError(f"{step_name} failed: {exc}") from exc

        if transformed == current:
            logger.info("%s made no clipboard changes.", step_name)
            continue

        write_clipboard_text(transformed)
        logger.info(
            "%s updated clipboard (%s -> %s characters).",
            step_name,
            len(current),
            len(transformed),
        )
        current = transformed

    logger.info("%s finished clipboard pipeline.", command_name)
