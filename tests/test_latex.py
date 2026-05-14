"""Library tests for LaTeX file loading and include traversal.

The tests use real temporary TeX files and the public library functions. CLI
argument parsing, backup behavior, and complete TeX parsing are out of scope.
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
TOOLKIT = SRC / "latex-toolkit"
if str(TOOLKIT) not in sys.path:
    sys.path.insert(0, str(TOOLKIT))

from lib.core import TexFile, read_tex_file, write_tex_file  # noqa: E402
from lib.latex import expand_includes, walk_tex_sources  # noqa: E402


class LatexLibraryTests(TestCase):
    def test_read_tex_file_returns_named_texfile(self) -> None:
        """Reading a TeX file preserves its source text and resolved filename."""

        with TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "paper.tex"
            source.write_text("hello\n", encoding="utf-8")

            tex_file = read_tex_file(source)

            self.assertEqual(tex_file.code, "hello\n")
            self.assertEqual(tex_file.filename, source.resolve())

    def test_write_tex_file_requires_destination_for_anonymous_buffer(self) -> None:
        """Anonymous generated buffers require an explicit destination path."""

        with self.assertRaises(ValueError):
            write_tex_file(TexFile.anonymous("generated"))

    def test_expand_includes_returns_anonymous_texfile(self) -> None:
        """Expanded include output is returned as generated anonymous TeX."""

        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            (work / "chapter.tex").write_text("Section body.\n", encoding="utf-8")
            main = work / "main.tex"
            main.write_text("Intro\n\\input{chapter}\nDone\n", encoding="utf-8")

            expanded = expand_includes(main)

            self.assertIsNone(expanded.filename)
            self.assertEqual(expanded.code, "Intro\nSection body.\nDone\n")

    def test_expand_includes_supports_subfile_commands(self) -> None:
        """Include expansion follows subfile document-body semantics."""

        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            (work / "nested.tex").write_text("Nested body.\n", encoding="utf-8")
            (work / "chapter.tex").write_text(
                "\\documentclass[main]{subfiles}\n"
                "\\begin{document}\n"
                "Section body.\n"
                "\\subfileinclude{nested}\n"
                "\\end{document}\n"
                "Ignored tail.\n",
                encoding="utf-8",
            )
            main = work / "main.tex"
            main.write_text(
                "\\documentclass{article}\n"
                "\\usepackage{subfiles}\n"
                "\\begin{document}\n"
                "Intro\n"
                "\\subfile{chapter}\n"
                "Done\n"
                "\\end{document}\n",
                encoding="utf-8",
            )

            expanded = expand_includes(main)

            self.assertEqual(
                expanded.code,
                "\\documentclass{article}\n"
                "\\usepackage{subfiles}\n"
                "\\begin{document}\n"
                "Intro\n"
                "Section body.\n"
                "Nested body.\n"
                "Done\n"
                "\\end{document}\n",
            )

    def test_walk_tex_sources_follows_subfile_commands(self) -> None:
        """Source walking returns the root and recursively included subfiles."""

        with TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            nested = work / "nested.tex"
            chapter = work / "chapter.tex"
            main = work / "main.tex"
            nested.write_text("Nested body.\n", encoding="utf-8")
            chapter.write_text(
                "\\documentclass[main]{subfiles}\n"
                "\\begin{document}\n"
                "\\input{nested}\n"
                "\\end{document}\n",
                encoding="utf-8",
            )
            main.write_text(
                "\\documentclass{article}\n"
                "\\usepackage{subfiles}\n"
                "\\begin{document}\n"
                "\\subfile{chapter}\n"
                "\\end{document}\n",
                encoding="utf-8",
            )

            walked = walk_tex_sources(main)

            self.assertEqual(walked, [main.resolve(), chapter.resolve(), nested.resolve()])
