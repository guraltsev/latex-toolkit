#!/usr/bin/env python3
r"""CLI for normalizing TeXmacs vertical-bar delimiters."""

from __future__ import annotations

from pathlib import Path
import argparse
import re

from lib.backup import DEFAULT_BACKUP_DIR, backup_file
from lib.latex import read_text, split_comment, write_text
from lib.latex_parser import split_document_regions
from lib.logging_config import run_clipboard_transform, run_command

# This command overwrites source files unless output or clipboard mode is used.
OVERWRITES_SOURCE_TEX = True

# Left-sized delimiter controls should use the left double-bar delimiter.
_LEFT_DELIMITER_CONTROLS = frozenset({"left", "bigl", "Bigl", "biggl", "Biggl"})

# Right-sized delimiter controls should use the right double-bar delimiter.
_RIGHT_DELIMITER_CONTROLS = frozenset({"right", "bigr", "Bigr", "biggr", "Biggr"})

# Neutral-sized delimiter controls do not imply an opening or closing side.
_NEUTRAL_DELIMITER_CONTROLS = frozenset(
    {
        "middle",
        "big",
        "Big",
        "bigg",
        "Bigg",
        "bigm",
        "Bigm",
        "biggm",
        "Biggm",
    }
)

# Match size controls immediately followed by the ``\|`` delimiter symbol.
_SIZED_DOUBLE_BAR_RE = re.compile(
    r"\\(?P<control>"
    r"Biggl|biggl|Biggr|biggr|"
    r"Bigl|bigl|Bigr|bigr|"
    r"Biggm|biggm|Bigg|bigg|Bigm|bigm|Big|big|"
    r"left|right|middle"
    r")\s*\\\|"
)

# A replacement control word needs a token boundary before another macro letter.
_CONTROL_WORD_FOLLOW_RE = re.compile(r"[A-Za-z@]")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="texmacs_vert_delimiters",
        description=(
            "Rewrite sized \\| delimiters as explicit \\lVert, \\rVert, or \\Vert. "
            "By default the input file is overwritten; use -o/--output to write elsewhere."
        ),
    )
    parser.add_argument("input", nargs="?", help="Input .tex file.")
    parser.add_argument(
        "--clipboard",
        action="store_true",
        help="Read LaTeX from the clipboard and replace it with converted output.",
    )
    parser.add_argument(
        "-o",
        "--output",
        "--output-file",
        dest="output",
        help="Write converted output to this path instead of overwriting the input file.",
    )
    parser.add_argument(
        "-B",
        "--no-backup",
        action="store_true",
        help="Do not create a backup before overwriting the input file.",
    )
    parser.add_argument(
        "--backup-dir",
        default=DEFAULT_BACKUP_DIR,
        help="Relative or absolute directory for backups when overwriting. Default: %(default)s",
    )
    return parser


def transform_text(text: str) -> str:
    r"""Rewrite sized ``\|`` delimiters in ``text`` for TeXmacs.

    Parameters
    ----------
    text : str
        LaTeX source text to transform.

    Returns
    -------
    str
        Source text with ``\left\|``-style delimiters rewritten to explicit
        ``\left \lVert``-style delimiter forms.
    """

    preamble, begin_doc, body, end_doc, postamble = split_document_regions(text)
    if begin_doc and end_doc:
        converted_body = _convert_sized_double_bars(body)
        return f"{preamble}{begin_doc}{converted_body}{end_doc}{postamble}"
    return _convert_sized_double_bars(text)


def main(argv: list[str] | None = None) -> int:
    def run() -> int:
        parser = build_parser()
        args = parser.parse_args(argv)

        if args.clipboard:
            if args.input is not None or args.output is not None:
                parser.error("--clipboard cannot be combined with input or output paths.")
            run_clipboard_transform("texmacs_vert_delimiters", transform_text)
            return 0

        if args.input is None:
            parser.error("the following arguments are required: input")

        input_path = Path(args.input).expanduser().resolve()
        converted = transform_text(read_text(input_path))
        output_path = Path(args.output).expanduser().resolve() if args.output else input_path

        if output_path == input_path and not args.no_backup:
            backup_file(input_path, args.backup_dir)

        write_text(output_path, converted)
        return 0

    return run_command("texmacs_vert_delimiters", run)


def _convert_sized_double_bars(text: str) -> str:
    converted_lines: list[str] = []

    # Rewrite only the code portion of each line so commented source remains
    # source-preserving even when it contains delimiter-looking text.
    for line in text.splitlines(keepends=True):
        code, comment = split_comment(line)
        converted_lines.append(_SIZED_DOUBLE_BAR_RE.sub(_replacement_delimiter, code))
        converted_lines.append(comment)

    return "".join(converted_lines)


def _replacement_delimiter(match: re.Match[str]) -> str:
    control = match.group("control")
    if control in _LEFT_DELIMITER_CONTROLS:
        delimiter = r"\lVert"
    elif control in _RIGHT_DELIMITER_CONTROLS:
        delimiter = r"\rVert"
    elif control in _NEUTRAL_DELIMITER_CONTROLS:
        delimiter = r"\Vert"
    else:  # pragma: no cover - the regex and control sets are kept in sync.
        return match.group(0)

    replacement = "\\" + control + " " + delimiter
    if _needs_trailing_control_word_boundary(match.string, match.end()):
        return replacement + " "
    return replacement


def _needs_trailing_control_word_boundary(text: str, index: int) -> bool:
    return index < len(text) and _CONTROL_WORD_FOLLOW_RE.fullmatch(text[index]) is not None


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
