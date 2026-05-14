"""Library tests for titled ``proof*`` and ``proof`` conversion.

The tests call the public text conversion function and assert observable LaTeX
rewrites. CLI write policy and low-level tokenizer spans are out of scope.
"""

from __future__ import annotations

from pathlib import Path
from unittest import TestCase
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
TOOLKIT = SRC / "latex-toolkit"
if str(TOOLKIT) not in sys.path:
    sys.path.insert(0, str(TOOLKIT))

from lib.proofstar import convert_text  # noqa: E402


class ProofstarLibraryTests(TestCase):
    def test_titled_proofstar_is_rewritten_in_document_body(self) -> None:
        """Titled proofstar environments become proof environments in document bodies."""

        source = (
            "\\documentclass{article}\n"
            "\\newcommand{\\keep}{\\begin{proof*}{Preamble}p\\end{proof*}}\n"
            "\\begin{document}\n"
            "\\begin{proof*}{POOF}\n"
            "  strs\n"
            "\\end{proof*}\n"
            "% \\begin{proof*}{Comment}ignored\\end{proof*}\n"
            "\\end{document}\n"
            "\\begin{proof*}{Tail}tail\\end{proof*}\n"
        )

        converted = convert_text(source)

        self.assertEqual(
            converted,
            "\\documentclass{article}\n"
            "\\newcommand{\\keep}{\\begin{proof*}{Preamble}p\\end{proof*}}\n"
            "\\begin{document}\n"
            "\\begin{proof}[POOF]\n"
            "strs\n"
            "\\end{proof}\n"
            "% \\begin{proof*}{Comment}ignored\\end{proof*}\n"
            "\\end{document}\n"
            "\\begin{proof*}{Tail}tail\\end{proof*}\n",
        )

    def test_untitled_or_unmatched_proofstar_is_preserved(self) -> None:
        """Untitled or incomplete proofstar snippets remain unchanged."""

        source = (
            "\\begin{proof*}no title\\end{proof*}\n"
            "\\begin{proof*}{Missing end}\n"
        )

        converted = convert_text(source)

        self.assertEqual(converted, source)

    def test_titled_proof_is_rewritten_back_to_proofstar_in_document_body(self) -> None:
        """Titled proof environments become proofstar environments in document bodies."""

        source = (
            "\\documentclass{article}\n"
            "\\newcommand{\\keep}{\\begin{proof}[Preamble]p\\end{proof}}\n"
            "\\begin{document}\n"
            "\\begin{proof}[POOF]\n"
            "strs\n"
            "\\end{proof}\n"
            "\\begin{proof}[Proof of {A]}]\n"
            "body\n"
            "\\end{proof}\n"
            "\\begin{proof}untitled\\end{proof}\n"
            "% \\begin{proof}[Comment]ignored\\end{proof}\n"
            "\\end{document}\n"
            "\\begin{proof}[Tail]tail\\end{proof}\n"
        )

        converted = convert_text(source, reverse=True)

        self.assertEqual(
            converted,
            "\\documentclass{article}\n"
            "\\newcommand{\\keep}{\\begin{proof}[Preamble]p\\end{proof}}\n"
            "\\begin{document}\n"
            "\\begin{proof*}{POOF}\n"
            "strs\n"
            "\\end{proof*}\n"
            "\\begin{proof*}{Proof of {A]}}\n"
            "body\n"
            "\\end{proof*}\n"
            "\\begin{proof}untitled\\end{proof}\n"
            "% \\begin{proof}[Comment]ignored\\end{proof}\n"
            "\\end{document}\n"
            "\\begin{proof}[Tail]tail\\end{proof}\n",
        )
