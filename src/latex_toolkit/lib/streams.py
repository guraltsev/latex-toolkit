"""Configure standard text streams used by command-line transforms."""

from __future__ import annotations

import sys


def configure_utf8_standard_streams() -> None:
    """Set reconfigurable process standard text streams to UTF-8."""
    # Standard streams inherit the active Windows code page unless the process
    # chooses an encoding.  Preserve in-memory test streams that lack this API.
    for stream in (sys.stdin, sys.stdout):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8")
