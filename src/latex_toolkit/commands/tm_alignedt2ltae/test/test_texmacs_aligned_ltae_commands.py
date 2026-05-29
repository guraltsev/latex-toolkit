"""Command tests for strict TeXmacs ``aligned`` to ``ltae`` conversion.

The tests invoke the real CLI command against a temporary file and check
user-visible output plus backup side effects. Parser implementation details are
out of scope.
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
import subprocess
import sys

from test_support import pythonpath_env


class TexmacsAlignedLtaeCommandTests(TestCase):
    def run_cli(self, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        """Run a latex-toolkit command with the checkout source on ``PYTHONPATH``."""

        command_name, *command_args = args
        return subprocess.run(
            [sys.executable, "-m", f"latex_toolkit.commands.{command_name}", *command_args],
            cwd=str(cwd) if cwd is not None else None,
            env=pythonpath_env(),
            text=True,
            capture_output=True,
            check=False,
        )

    def test_tm_alignedt2ltae_overwrites_with_expected_output_and_backup(self) -> None:
        """The command overwrites converted files and keeps a backup."""

        source = "<aligned|t|<tformat|<table|<row|<cell|>|<cell|x>>>>>\n"
        expected = "<ltae|<tformat|<table|<row|<cell|x>>>>>\n"

        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            input_path = work / "fragment.tm"
            input_path.write_text(source, encoding="utf-8")

            result = self.run_cli("tm_alignedt2ltae", str(input_path))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(input_path.read_text(encoding="utf-8"), expected)
            backups = sorted((work / ".backup").iterdir())
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), source)

    def test_tm_alignedt2ltae_preserves_unicode_text_when_overwriting(self) -> None:
        """The command preserves Unicode text while rewriting TeXmacs tables."""

        unicode_text = "H\u00f6lder \u03b1"
        source = f"<aligned|t|<tformat|<table|<row|<cell|>|<cell|{unicode_text}>>>>>\n"
        expected = f"<ltae|<tformat|<table|<row|<cell|{unicode_text}>>>>>\n"

        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            input_path = work / "unicode.tm"
            input_path.write_text(source, encoding="utf-8")

            result = self.run_cli("tm_alignedt2ltae", str(input_path))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(input_path.read_text(encoding="utf-8"), expected)

    def test_tm_alignedt2ltae_overwrites_readable_tmu_source(self) -> None:
        """The tm command converts readable .tmu documents and keeps a backup."""

        source = (
            "<subsection|Coefficient upper bounds for H\u00f6lder spaces>\n\n"
            "<\\equation>\n"
            "  <label|eq:holder-analysis-nonhomogeneous-upper>"
            "<aligned|t|<tformat|<table|"
            "<row|<cell|>|<cell|sup<rsub|\\<psi\\>> t<rsup|-\\<alpha\\>>>>|"
            "<row|<cell|>|<cell|\\<lesssim\\><rsub|d,\\<alpha\\>>"
            "<around|\\<\\|\\|\\>|f|\\<\\|\\|\\>>>>"
            ">>>\n"
            "</equation>\n"
        )
        expected = (
            "<subsection|Coefficient upper bounds for H\u00f6lder spaces>\n\n"
            "<\\equation>\n"
            "  <label|eq:holder-analysis-nonhomogeneous-upper>"
            "<ltae|<tformat|<table|"
            "<row|<cell|sup<rsub|\\<psi\\>> t<rsup|-\\<alpha\\>>>>|"
            "<row|<cell|\\<lesssim\\><rsub|d,\\<alpha\\>>"
            "<around|\\<\\|\\|\\>|f|\\<\\|\\|\\>>>>"
            ">>>\n"
            "</equation>\n"
        )

        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            input_path = work / "fragment.tmu"
            input_path.write_text(source, encoding="utf-8")

            result = self.run_cli("tm_alignedt2ltae", str(input_path))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(input_path.read_text(encoding="utf-8"), expected)
            backups = sorted((work / ".backup").iterdir())
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), source)
