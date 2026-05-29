"""Shared helpers for test modules in the repository root and src tree."""

from __future__ import annotations

from pathlib import Path
import os
import sys

REPO_ROOT = Path(__file__).resolve().parent
SRC_ROOT = REPO_ROOT / "src"
FIXTURES_ROOT = REPO_ROOT / "tests" / "fixtures"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


def pythonpath_env() -> dict[str, str]:
    """Return an environment that imports package modules from ``src``."""

    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC_ROOT)
    return env
