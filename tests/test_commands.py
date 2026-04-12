from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "src" / "lt_cli.py"


class CommandTests(TestCase):
    def run_cli(self, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CLI), *args],
            cwd=str(cwd) if cwd is not None else None,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_expand_includes_stdout(self) -> None:
        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            (work / "chapter.tex").write_text("Section body.\n", encoding="utf-8")
            (work / "main.tex").write_text("Intro\n\\input{chapter}\nDone\n", encoding="utf-8")

            result = self.run_cli("expand-includes", str(work / "main.tex"))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "Intro\nSection body.\nDone\n")

    def test_strip_comments_in_place_creates_backup(self) -> None:
        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            source = work / "paper.tex"
            source.write_text("keep \\% literal % drop me\n", encoding="utf-8")

            result = self.run_cli("strip-comments", str(source), "--in-place")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(source.read_text(encoding="utf-8"), "keep \\% literal \n")
            backup_dir = work / ".lt-backup"
            backups = sorted(path.name for path in backup_dir.iterdir())
            self.assertEqual(len(backups), 1)
            self.assertTrue(backups[0].startswith("paper.tex.backup."))

    def test_list_graphics_recursive_unique(self) -> None:
        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            (work / "figs.tex").write_text(
                "\\includegraphics{figures/a.pdf}\n\\includegraphics{figures/a.pdf}\n",
                encoding="utf-8",
            )
            (work / "main.tex").write_text("\\input{figs}\n", encoding="utf-8")

            result = self.run_cli("list-graphics", str(work / "main.tex"), "--unique")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.splitlines(), ["figures/a.pdf"])
