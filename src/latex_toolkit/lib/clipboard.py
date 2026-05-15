"""Read and write plain text from the system clipboard.

The helpers use ``pyperclip`` because it behaves reliably with desktop
clipboard managers such as CopyQ. A ``RuntimeError`` is raised when the
``pyperclip`` backend cannot read or write text.
"""

from __future__ import annotations

import pyperclip


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

    try:
        return str(pyperclip.paste())
    except pyperclip.PyperclipException as exc:
        raise RuntimeError(f"pyperclip clipboard reader failed: {exc}") from exc


def write_clipboard_text(text: str) -> None:
    """Replace the current clipboard contents with ``text``.

    Parameters
    ----------
    text : str
        Text to place in the system clipboard.

    Returns
    -------
    None
        The system clipboard is replaced with ``text``.

    Raises
    ------
    RuntimeError
        No supported clipboard writer is available or the writer fails.
    """

    try:
        pyperclip.copy(text)
    except pyperclip.PyperclipException as exc:
        raise RuntimeError(f"pyperclip clipboard writer failed: {exc}") from exc
