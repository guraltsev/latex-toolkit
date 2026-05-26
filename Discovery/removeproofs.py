#!/usr/bin/env python3
"""Legacy wrapper for the ``removeproofs`` command package."""

from __future__ import annotations

from latex_toolkit.commands.removeproofs.main import main, transform_text

remove_proof_environments = transform_text


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
