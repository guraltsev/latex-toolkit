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

    def test_expand_includes_default_overwrite_creates_backup(self) -> None:
        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            chapter = work / "chapter.tex"
            main = work / "main.tex"
            chapter.write_text("Section body.\n", encoding="utf-8")
            original_main = "Intro\n\\input{chapter}\nDone\n"
            main.write_text(original_main, encoding="utf-8")

            result = self.run_cli("expand-includes", str(main))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "")
            self.assertEqual(main.read_text(encoding="utf-8"), "Intro\nSection body.\nDone\n")
            backup_dir = work / ".lt-backup"
            backups = sorted(backup_dir.iterdir())
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), original_main)

    def test_expand_includes_output_preserves_source(self) -> None:
        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            chapter = work / "chapter.tex"
            main = work / "main.tex"
            output = work / "flat.tex"
            chapter.write_text("Section body.\n", encoding="utf-8")
            original_main = "Intro\n\\input{chapter}\nDone\n"
            main.write_text(original_main, encoding="utf-8")

            result = self.run_cli("expand-includes", str(main), "-o", str(output))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(main.read_text(encoding="utf-8"), original_main)
            self.assertEqual(output.read_text(encoding="utf-8"), "Intro\nSection body.\nDone\n")
            self.assertFalse((work / ".lt-backup").exists())

    def test_strip_comments_default_overwrite_creates_backup(self) -> None:
        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            source = work / "paper.tex"
            original = "keep \\% literal % drop me\n"
            source.write_text(original, encoding="utf-8")

            result = self.run_cli("strip-comments", str(source))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(source.read_text(encoding="utf-8"), "keep \\% literal \n")
            backup_dir = work / ".lt-backup"
            backups = sorted(backup_dir.iterdir())
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), original)

    def test_list_graphics_recursive_unique_across_subfiles(self) -> None:
        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            (work / "morefigs.tex").write_text("\\includegraphics{figures/b.pdf}\n", encoding="utf-8")
            (work / "figs.tex").write_text(
                "\\documentclass[main]{subfiles}\n"
                "\\includegraphics{figures/preamble-only.pdf}\n"
                "\\begin{document}\n"
                "\\includegraphics{figures/a.pdf}\n"
                "\\includegraphics{figures/a.pdf}\n"
                "\\input{morefigs}\n"
                "\\end{document}\n"
                "\\includegraphics{figures/trailing-only.pdf}\n",
                encoding="utf-8",
            )
            (work / "main.tex").write_text(
                "\\documentclass{article}\n"
                "\\usepackage{subfiles}\n"
                "\\begin{document}\n"
                "\\subfile{figs}\n"
                "\\end{document}\n",
                encoding="utf-8",
            )

            result = self.run_cli("list-graphics", str(work / "main.tex"), "--unique")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.splitlines(), ["figures/a.pdf", "figures/b.pdf"])
