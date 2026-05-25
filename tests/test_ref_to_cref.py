"""Command transform tests for singular named-reference cleveref rewrites.

The tests call the command's public text transform and assert only the
observable LaTeX replacements. CLI write policy and clipboard integration are
out of scope.
"""

from __future__ import annotations

from pathlib import Path
from unittest import TestCase
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from latex_toolkit.commands.ref_to_cref.main import transform_text  # noqa: E402


class RefToCrefTransformTests(TestCase):
    def test_matching_singular_named_refs_become_cref_commands(self) -> None:
        """Eligible singular noun-plus-ref phrases become capitalization-matched cleverefs."""

        source = (
            "Proposition~\\ref{prop:main} and Proposition \\ref{prop:alt}.\n"
            "proposition~\\ref{prop:lower} and proposition \\ref{prop:space}.\n"
            "Lemma~\\ref{lem:key}, lemma \\ref{lemma:minor}.\n"
            "Corollary \\ref{corr:branch}, corollary~\\ref{cor:leaf}.\n"
            "Theorem~\\ref{thm:one}, theorem \\ref{theorem:two}.\n"
            "Remark \\ref{rmk:note}, remark~\\ref{rem:aside}.\n"
        )

        converted = transform_text(source)

        self.assertEqual(
            converted,
            "\\Cref{prop:main} and \\Cref{prop:alt}.\n"
            "\\cref{prop:lower} and \\cref{prop:space}.\n"
            "\\Cref{lem:key}, \\cref{lemma:minor}.\n"
            "\\Cref{corr:branch}, \\cref{cor:leaf}.\n"
            "\\Cref{thm:one}, \\cref{theorem:two}.\n"
            "\\Cref{rmk:note}, \\cref{rem:aside}.\n"
        )

    def test_nonmatching_prefixes_plurals_and_spacing_are_preserved(self) -> None:
        """Only the exact supported noun forms, separators, and label prefixes are rewritten."""

        source = (
            "Propositions~\\ref{prop:many}\n"
            "Proposition\\ref{prop:tight}\n"
            "Proposition\t\\ref{prop:tabbed}\n"
            "Proposition ~\\ref{prop:spaced-tilde}\n"
            "Proposition \\ref{lemma:not-prop}\n"
            "Corollary \\ref{corollary:spelled-right}\n"
            "Remark \\ref{remark:full-word}\n"
            "LEMMA \\ref{lem:loud}\n"
        )

        converted = transform_text(source)

        self.assertEqual(converted, source)
