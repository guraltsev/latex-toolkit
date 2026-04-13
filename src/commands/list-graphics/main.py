#!/usr/bin/env python3
"""CLI for listing LaTeX includegraphics targets."""

from __future__ import annotations

from pathlib import Path
import argparse
import sys

from lib.core import read_tex_file
from lib.latex import extract_graphics_targets, walk_tex_documents

OVERWRITES_SOURCE_TEX = False


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="list-graphics",
        description="List \\includegraphics targets from a LaTeX source tree.",
    )
    parser.add_argument("input", help="Root .tex file to inspect.")
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Only inspect the root file instead of walking included files.",
    )
    parser.add_argument(
        "--unique",
        action="store_true",
        help="Only print each graphics target once.",
    )
    parser.add_argument(
        "--with-source",
        action="store_true",
        help="Prefix each graphics target with the file where it was found.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    input_path = Path(args.input).expanduser().resolve()
    sources = [read_tex_file(input_path)] if args.no_recursive else walk_tex_documents(input_path)

    seen: set[str] = set()
    for source in sources:
        source_path = source.filename if source.filename is not None else input_path
        for target in extract_graphics_targets(source.code):
            rendered = f"{source_path}: {target}" if args.with_source else target
            if args.unique and rendered in seen:
                continue
            seen.add(rendered)
            sys.stdout.write(f"{rendered}\n")

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
