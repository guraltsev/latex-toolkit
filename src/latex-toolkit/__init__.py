"""Source-checkout command modules are available for ``python -m`` execution."""

from __future__ import annotations

from pathlib import Path
import sys

_package_root = Path(__file__).resolve().parent

# Command modules keep using top-level ``lib`` imports so each command folder
# can still be copied beside a sibling ``lib`` directory and run independently.
_package_root_text = str(_package_root)
if _package_root_text not in sys.path:
    sys.path.insert(0, _package_root_text)

# Let ``python -m latex-toolkit.strip-comments`` resolve command packages from
# the same directory used by ``python -m latex-toolkit.commands.strip-comments``.
_commands_root_text = str(_package_root / "commands")
if _commands_root_text not in __path__:
    __path__.append(_commands_root_text)

__all__: list[str] = []
