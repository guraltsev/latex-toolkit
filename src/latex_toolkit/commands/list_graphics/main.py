#!/usr/bin/env python3
"""CLI for listing LaTeX includegraphics targets."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from pathlib import Path
import argparse

from latex_toolkit.lib.core import read_tex_file
from latex_toolkit.lib.latex import extract_graphics_targets, walk_tex_documents
from latex_toolkit.lib.logging_config import run_clipboard_transform, run_command

# This command reports targets and never overwrites source TeX files.
OVERWRITES_SOURCE_TEX = False


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="list-graphics",
        description="List \\includegraphics targets from a LaTeX source tree.",
    )
    parser.add_argument("input", nargs="?", help="Root .tex file to inspect.")
    parser.add_argument(
        "--clipboard",
        action="store_true",
        help="Read LaTeX from the clipboard and replace it with listed graphics targets.",
    )
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


def transform_text(text: str, *, unique: bool = False, with_source: bool = False) -> str:
    """List graphics targets in ``text`` as newline-delimited output.

    Parameters
    ----------
    text : str
        LaTeX source text to inspect.
    unique : bool
        Whether repeated rendered targets should be emitted only once.
    with_source : bool
        Whether each target should be prefixed with ``<clipboard>``.

    Returns
    -------
    str
        Newline-delimited graphics targets.
    """

    lines = _render_targets(
        ((Path("<clipboard>"), extract_graphics_targets(text)),),
        unique=unique,
        with_source=with_source,
    )
    return "\n".join(lines) + ("\n" if lines else "")


def main(argv: list[str] | None = None) -> int:
    def run() -> int:
        parser = build_parser()
        args = parser.parse_args(argv)

        if args.clipboard:
            if args.input is not None:
                parser.error("--clipboard cannot be combined with an input path.")
            run_clipboard_transform(
                "list-graphics",
                lambda text: transform_text(
                    text,
                    unique=args.unique,
                    with_source=args.with_source,
                ),
            )
            return 0

        if args.input is None:
            parser.error("the following arguments are required: input")

        input_path = Path(args.input).expanduser().resolve()
        sources = [read_tex_file(input_path)] if args.no_recursive else walk_tex_documents(input_path)

        # Render all discovered targets before writing so uniqueness behavior is
        # shared between file and clipboard modes.
        source_targets = (
            (
                source.filename if source.filename is not None else input_path,
                extract_graphics_targets(source.code),
            )
            for source in sources
        )
        for rendered in _render_targets(source_targets, unique=args.unique, with_source=args.with_source):
            print(rendered)

        return 0

    return run_command("list-graphics", run)


def _render_targets(
    source_targets: Iterable[tuple[Path, Sequence[str]]],
    *,
    unique: bool,
    with_source: bool,
) -> list[str]:
    """Return rendered graphics target lines from source-target pairs."""

    seen: set[str] = set()
    rendered_lines: list[str] = []

    for source_path, targets in source_targets:
        for target in targets:
            rendered = f"{source_path}: {target}" if with_source else target
            if unique and rendered in seen:
                continue
            seen.add(rendered)
            rendered_lines.append(rendered)

    return rendered_lines


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
