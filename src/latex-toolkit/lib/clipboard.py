"""Read and write plain text from the system clipboard.

The helpers use platform clipboard commands that are commonly available on
Windows, macOS, Wayland, and X11 desktops. A ``RuntimeError`` is raised when no
supported clipboard command is available or the selected command fails.
"""

from __future__ import annotations

from collections.abc import Sequence
import os
import shutil
import subprocess


def read_clipboard_text() -> str:
    """Return the current clipboard contents as text.

    Returns
    -------
    str
        Text currently stored in the system clipboard.

    Raises
    ------
    RuntimeError
        No supported clipboard reader is available or the reader fails.
    """

    for command in _reader_commands():
        if _command_exists(command[0]):
            return _run_clipboard_command(command)

    raise RuntimeError("No supported clipboard reader was found.")


def write_clipboard_text(text: str) -> None:
    """Replace the current clipboard contents with ``text``.

    Parameters
    ----------
    text : str
        Text to place in the system clipboard.

    Raises
    ------
    RuntimeError
        No supported clipboard writer is available or the writer fails.
    """

    for command in _writer_commands():
        if _command_exists(command[0]):
            _run_clipboard_command(command, input_text=text)
            return

    raise RuntimeError("No supported clipboard writer was found.")


def _reader_commands() -> tuple[tuple[str, ...], ...]:
    """Return platform-preferred clipboard reader commands."""

    if os.name == "nt":
        return (("powershell", "-NoProfile", "-Command", "Get-Clipboard -Raw"),)
    if _sys_platform() == "darwin":
        return (("pbpaste",),)
    return (
        ("wl-paste", "--no-newline"),
        ("xclip", "-selection", "clipboard", "-out"),
        ("xsel", "--clipboard", "--output"),
    )


def _writer_commands() -> tuple[tuple[str, ...], ...]:
    """Return platform-preferred clipboard writer commands."""

    if os.name == "nt":
        return (("powershell", "-NoProfile", "-Command", "Set-Clipboard"),)
    if _sys_platform() == "darwin":
        return (("pbcopy",),)
    return (
        ("wl-copy",),
        ("xclip", "-selection", "clipboard", "-in"),
        ("xsel", "--clipboard", "--input"),
    )


def _command_exists(executable: str) -> bool:
    """Return whether ``executable`` can be found on ``PATH``."""

    return shutil.which(executable) is not None


def _run_clipboard_command(command: Sequence[str], *, input_text: str | None = None) -> str:
    """Run one clipboard command and return its stdout text."""

    result = subprocess.run(
        list(command),
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode == 0:
        return result.stdout

    detail = result.stderr.strip() or result.stdout.strip() or "clipboard command failed"
    raise RuntimeError(detail)


def _sys_platform() -> str:
    """Return the Python platform name used for clipboard selection."""

    import sys

    return sys.platform
