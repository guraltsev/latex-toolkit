#!/usr/bin/env python3
"""CLI for manually reformatting LaTeX math environments."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
import argparse
import importlib
import importlib.util
import subprocess
import sys

from latex_toolkit.lib.backup import DEFAULT_BACKUP_DIR, backup_file
from latex_toolkit.lib.latex import read_text, write_text
from latex_toolkit.lib.logging_config import run_clipboard_transform, run_command

# Install the parser dependency into a user-writable cache when it is missing.
PYLATEXENC_PACKAGE = "pylatexenc"

# These display-math environments are reformatted in place; nested environments
# outside this set are traversed but not directly rewritten.
MATH_ENVIRONMENTS = {
    "align",
    "align*",
    "alignat",
    "alignat*",
    "equation",
    "equation*",
    "gather",
    "gather*",
    "multline",
    "multline*",
    "flalign",
    "flalign*",
    "math",
    "displaymath",
}

# These nested math environments keep their original source because their
# internal layout is usually more specialized than this formatter's rules.
NESTED_PRESERVED_ENVIRONMENTS = {
    "array",
    "Bmatrix",
    "bmatrix",
    "cases",
    "matrix",
    "pmatrix",
    "smallmatrix",
    "subarray",
    "Vmatrix",
    "vmatrix",
}

# Long lines prefer breaking at relation symbols before ordinary arithmetic.
RELATION_SYMBOLS = [
    "=",
    r"\lesssim",
    ">",
    "<",
    r"\approx",
    r"\eqdef",
    r"\eqd",
    ":=",
    r"\simeq",
    r"\eqsim",
    r"\cong",
    r"\sim",
    r"\leq",
    r"\geq",
    r"\leqslant",
    r"\geqslant",
    r"\le",
    r"\ge",
    r"\ll",
    r"\gg",
]
OPERATOR_SYMBOLS = ["+", "-", "*"]

# These macros keep their argument text literal with respect to spacing, even
# when they appear inside a math environment.
LITERAL_ARGUMENT_MACROS = {"label", "mbox", "text"}


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser.

    Returns
    -------
    argparse.ArgumentParser
        Parser configured for manual LaTeX math reformatting.
    """

    parser = argparse.ArgumentParser(
        prog="manual_latex_reformat",
        description=(
            "Reformat LaTeX math environments with compact manual-style spacing. "
            "With no input or output paths, the command processes clipboard text."
        ),
    )
    parser.add_argument("input", nargs="?", help="Input .tex file.")
    parser.add_argument(
        "--clipboard",
        action="store_true",
        help="Read LaTeX from the clipboard and replace it with reformatted output.",
    )
    parser.add_argument(
        "--max-width",
        type=int,
        default=95,
        help="Maximum formatted math line length before splitting. Default: %(default)s",
    )
    parser.add_argument(
        "-o",
        "--output",
        "--output-file",
        dest="output",
        help="Write reformatted output to this path instead of overwriting the input file.",
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


def transform_text(text: str, *, max_width: int = 95) -> str:
    """Reformat supported LaTeX math environments in ``text``.

    Parameters
    ----------
    text : str
        LaTeX source text to transform.
    max_width : int
        Maximum formatted math line length before splitting.

    Returns
    -------
    str
        Source text with supported math environments reformatted.

    Raises
    ------
    RuntimeError
        The LaTeX parser cannot be imported, installed, or used successfully.
    """

    if not text.strip():
        return text
    if max_width < 1:
        raise ValueError("max_width must be positive.")

    ensure_pylatexenc()
    from pylatexenc.latexwalker import LatexWalker

    try:
        nodelist, _, _ = LatexWalker(text).get_latex_nodes(0)
    except Exception as exc:  # pragma: no cover - dependent parser failure path
        raise RuntimeError(f"could not parse LaTeX: {exc}") from exc

    line_ending = _preferred_line_ending(text)
    replacements = _collect_replacements(
        nodelist,
        text,
        line_ending=line_ending,
        max_width=max_width,
    )
    if not replacements:
        return text

    # Apply replacements from the end of the source backward so earlier source
    # positions remain valid while each math body is rewritten.
    transformed = text
    for start, end, replacement in sorted(replacements, reverse=True):
        transformed = f"{transformed[:start]}{replacement}{transformed[end:]}"
    return transformed


def main(argv: list[str] | None = None) -> int:
    """Run the command-line workflow.

    Parameters
    ----------
    argv : list of str or None
        Command-line arguments to parse. ``None`` reads arguments from
        ``sys.argv``.

    Returns
    -------
    int
        Process exit status, with ``0`` for success and ``1`` for expected
        operational failures.

    Raises
    ------
    SystemExit
        Command-line arguments are invalid.
    """

    def run() -> int:
        parser = build_parser()
        args = parser.parse_args(argv)

        if args.max_width < 1:
            parser.error("--max-width must be positive.")

        # A missing input path means clipboard mode, matching the launchers
        # used for quick copied-LaTeX cleanup.
        use_clipboard = args.clipboard or (args.input is None and args.output is None)

        if use_clipboard:
            if args.input is not None or args.output is not None:
                parser.error("--clipboard cannot be combined with input or output paths.")
            run_clipboard_transform(
                "manual_latex_reformat",
                lambda text: transform_text(text, max_width=args.max_width),
            )
            return 0

        if args.input is None:
            parser.error("the following arguments are required: input")

        input_path = Path(args.input).expanduser().resolve()
        reformatted = transform_text(read_text(input_path), max_width=args.max_width)
        output_path = Path(args.output).expanduser().resolve() if args.output else input_path

        if output_path == input_path and not args.no_backup:
            backup_file(input_path, args.backup_dir)

        write_text(output_path, reformatted)
        return 0

    return run_command("manual_latex_reformat", run)


def ensure_pylatexenc() -> None:
    """Ensure that ``pylatexenc`` is importable, installing it when needed.

    Returns
    -------
    None
        The dependency is importable after the function returns.

    Raises
    ------
    RuntimeError
        The dependency cannot be imported or installed successfully.
    """

    install_root = _pylatexenc_install_root()
    if str(install_root) not in sys.path:
        sys.path.insert(0, str(install_root))

    if importlib.util.find_spec(PYLATEXENC_PACKAGE) is not None:
        return

    install_root.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--disable-pip-version-check",
        "--no-warn-script-location",
        "--upgrade",
        "--target",
        str(install_root),
        PYLATEXENC_PACKAGE,
    ]
    completed = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(_format_process_failure(f"could not install {PYLATEXENC_PACKAGE}", completed))

    importlib.invalidate_caches()
    if importlib.util.find_spec(PYLATEXENC_PACKAGE) is None:
        raise RuntimeError(
            f"{PYLATEXENC_PACKAGE} was installed into {install_root}, but the package is still not importable."
        )


def _collect_replacements(
    nodes: object,
    source: str,
    *,
    line_ending: str,
    max_width: int,
) -> list[tuple[int, int, str]]:
    """Collect source-span replacements for supported math environments."""

    replacements: list[tuple[int, int, str]] = []
    for node in nodes:
        if _is_target_math_container(node):
            body_span = _container_body_span(node)
            if body_span is None:
                continue
            start, end = body_span

            # Render math contents under the command's spacing rules, then
            # split only lines that exceed the configured length.
            formatted = _render_nodes_to_formatted_string(
                getattr(node, "nodelist", None),
                substack=False,
                start_of_line=True,
                max_width=max_width,
            )
            formatted, forced_leading_newline = _finalize_math_body(
                formatted,
                max_width=max_width,
                normalize_leading_label=True,
            )

            replacement = _restore_body_boundary_newlines(
                source[start:end],
                formatted,
                force_leading_newline=forced_leading_newline,
                line_ending=line_ending,
            )
            replacements.append((start, end, replacement))
            continue

        # Non-target nodes may still contain target environments deeper inside
        # groups, macro arguments, or other parsed child lists.
        nodelist = getattr(node, "nodelist", None)
        if nodelist is not None:
            replacements.extend(
                _collect_replacements(
                    nodelist,
                    source,
                    line_ending=line_ending,
                    max_width=max_width,
                )
            )
        for arg in _node_args(node):
            replacements.extend(
                _collect_replacements(
                    getattr(arg, "nodelist", []),
                    source,
                    line_ending=line_ending,
                    max_width=max_width,
                )
            )
    return replacements


def _restore_body_boundary_newlines(
    original_body: str,
    formatted_body: str,
    *,
    force_leading_newline: bool,
    line_ending: str,
) -> str:
    """Preserve environment-body newline separators around formatted content."""

    replacement = _apply_line_ending(formatted_body, line_ending)

    # Keep the structural newline after \begin{...} when the original display
    # body had one, while still letting the formatter remove indentation.
    leading_newline = _edge_newline(original_body, leading=True)
    if (force_leading_newline or leading_newline) and not replacement.startswith(("\n", "\r")):
        if not leading_newline:
            leading_newline = line_ending
        replacement = f"{leading_newline}{replacement}"

    # Keep the structural newline before \end{...}; avoid adding a second one
    # when the formatted body already ends after a row-break macro.
    trailing_newline = _edge_newline(original_body, leading=False)
    if trailing_newline and not replacement.endswith(("\n", "\r")):
        replacement = f"{replacement}{trailing_newline}"

    return replacement


def _preferred_line_ending(text: str) -> str:
    """Return the dominant line ending style from source text."""

    crlf_count = text.count("\r\n")
    bare_lf_count = text.count("\n") - crlf_count
    bare_cr_count = text.count("\r") - crlf_count

    if crlf_count >= bare_lf_count and crlf_count >= bare_cr_count and crlf_count > 0:
        return "\r\n"
    if bare_cr_count > bare_lf_count:
        return "\r"
    return "\n"


def _apply_line_ending(text: str, line_ending: str) -> str:
    """Return ``text`` rewritten to a specific line-ending convention."""

    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if line_ending == "\n":
        return normalized
    return normalized.replace("\n", line_ending)


def _edge_newline(text: str, *, leading: bool) -> str:
    """Return the first or last newline sequence at a text edge."""

    if not text:
        return ""

    if leading:
        if text.startswith("\r\n"):
            return "\r\n"
        if text.startswith(("\n", "\r")):
            return text[0]
        return ""

    if text.endswith("\r\n"):
        return "\r\n"
    if text.endswith(("\n", "\r")):
        return text[-1]
    return ""


def _render_nodes_to_formatted_string(
    nodes: object,
    *,
    substack: bool = False,
    start_of_line: bool = True,
    literal_text: bool = False,
    max_width: int,
) -> str:
    """Return formatted text for a list of pylatexenc nodes."""

    from pylatexenc.latexwalker import (
        LatexCharsNode,
        LatexCommentNode,
        LatexEnvironmentNode,
        LatexGroupNode,
        LatexMacroNode,
        LatexSpecialsNode,
    )

    result: list[str] = []
    last_char_was_space = False
    at_line_start = start_of_line
    pending_collapsed_space = False

    def append(text: str) -> None:
        nonlocal at_line_start, last_char_was_space
        if not text:
            return
        result.append(text)
        last_char_was_space = text.endswith((" ", "\n", "\t"))
        at_line_start = text.endswith("\n")

    for node in nodes:
        if pending_collapsed_space and _node_starts_visible_text(node):
            append(" ")
            pending_collapsed_space = False

        if isinstance(node, LatexCharsNode):
            at_line_start, last_char_was_space, pending_collapsed_space = _append_chars(
                node.chars,
                append,
                at_line_start=at_line_start,
                last_char_was_space=last_char_was_space,
                literal_text=literal_text,
            )
            continue

        if isinstance(node, LatexCommentNode):
            comment = getattr(node, "comment", "")
            append(comment if comment.startswith("%") else f"%{comment}")
            append("\n")
            last_char_was_space = False
            at_line_start = True
            pending_collapsed_space = False
            continue

        if isinstance(node, LatexSpecialsNode):
            specials = getattr(node, "specials_chars", "")
            if specials == "&":
                if not at_line_start and not last_char_was_space:
                    append(" ")
                append("& ")
                last_char_was_space = True
                at_line_start = False
            else:
                append(node.latex_verbatim())
                last_char_was_space = False
                at_line_start = False
            pending_collapsed_space = False
            continue

        if isinstance(node, LatexMacroNode):
            macro_name = node.macroname
            star = "*" if getattr(node, "star", None) == "*" else ""
            macro_text = rf"\{macro_name}{star}"

            if macro_name == "substack":
                append(r"\substack{")
                args = _node_args(node)
                if args:
                    append(
                        _render_nodes_to_formatted_string(
                            args[0].nodelist,
                            substack=True,
                            start_of_line=False,
                            max_width=max_width,
                        )
                    )
                append("}")
                last_char_was_space = False
                at_line_start = False
                pending_collapsed_space = False
                continue

            if macro_name == "\\":
                if substack:
                    append(rf"\\{star}")
                else:
                    if not at_line_start:
                        append("\n")
                    append(rf"\\{star}")
                    append("\n")
                    last_char_was_space = False
                    at_line_start = True
                pending_collapsed_space = False
                continue

            # Reconstruct ordinary macros so their arguments inherit the same
            # spacing rules without disturbing the macro name itself.
            append(macro_text)
            for arg in _node_args(node):
                opening, closing = _argument_delimiters(arg)
                append(opening)
                child_literal_text = literal_text or macro_name in LITERAL_ARGUMENT_MACROS
                append(
                    _render_nodes_to_formatted_string(
                        arg.nodelist,
                        substack=substack,
                        start_of_line=False,
                        literal_text=child_literal_text,
                        max_width=max_width,
                    )
                )
                append(closing)

            macro_post_space = getattr(node, "macro_post_space", "")
            if macro_post_space:
                at_line_start, last_char_was_space, pending_collapsed_space = _append_chars(
                    macro_post_space,
                    append,
                    at_line_start=at_line_start,
                    last_char_was_space=last_char_was_space,
                    literal_text=literal_text,
                )
            else:
                last_char_was_space = False
                at_line_start = False
            continue

        if isinstance(node, LatexGroupNode):
            append("{")
            append(
                _render_nodes_to_formatted_string(
                    node.nodelist,
                    substack=substack,
                    start_of_line=False,
                    literal_text=literal_text,
                    max_width=max_width,
                )
            )
            append("}")
            last_char_was_space = False
            at_line_start = False
            pending_collapsed_space = False
            continue

        if isinstance(node, LatexEnvironmentNode):
            environment_name = _environment_name(node)
            if environment_name not in NESTED_PRESERVED_ENVIRONMENTS:
                append(_render_nested_environment(node, max_width=max_width))
                last_char_was_space = False
                at_line_start = False
                pending_collapsed_space = False
                continue

            verbatim = node.latex_verbatim()
            append(verbatim)
            last_char_was_space = False
            at_line_start = verbatim.endswith("\n")
            pending_collapsed_space = False
            continue

        # Preserve any node type that this command does not deliberately
        # reformat, such as inline math or parser-specific extension nodes.
        verbatim = node.latex_verbatim()
        append(verbatim)
        last_char_was_space = False
        at_line_start = verbatim.endswith("\n")
        pending_collapsed_space = False

    return "".join(result)


def _append_chars(
    text: str,
    append: Callable[[str], None],
    *,
    at_line_start: bool,
    last_char_was_space: bool,
    literal_text: bool,
) -> tuple[bool, bool, bool]:
    """Append character text under the math spacing rules."""

    pending_collapsed_space = False
    text_length = len(text)
    for index, char in enumerate(text):
        if literal_text:
            if char in {"\n", "\r"}:
                next_char = _next_visible_char(text, index + 1)
                if not at_line_start and not last_char_was_space and next_char is not None:
                    append(" ")
                    last_char_was_space = True
                elif not at_line_start and not last_char_was_space and next_char is None:
                    pending_collapsed_space = True
                continue

            if at_line_start and char == " ":
                continue

            append(char)
            last_char_was_space = char in {" ", "\t"}
            at_line_start = False
            continue

        if char == "&":
            if not at_line_start and not last_char_was_space:
                append(" ")
            append("& ")
            last_char_was_space = True
            at_line_start = False
            continue

        if char in OPERATOR_SYMBOLS:
            if not last_char_was_space:
                append(" ")
            append(char)
            append(" ")
            last_char_was_space = True
            at_line_start = False
            continue

        if char in {"\n", "\r"}:
            next_char = _next_visible_char(text, index + 1)
            if not at_line_start and not last_char_was_space and next_char is not None:
                append(" ")
                last_char_was_space = True
            elif not at_line_start and not last_char_was_space and next_char is None:
                pending_collapsed_space = True
            continue

        if char in {" ", "\t"}:
            if at_line_start or last_char_was_space:
                continue
            append(" ")
            last_char_was_space = True
            at_line_start = False
            continue

        if at_line_start and char == " ":
            continue

        append(char)
        last_char_was_space = False
        at_line_start = False

    return at_line_start, last_char_was_space, pending_collapsed_space


def _next_visible_char(text: str, start: int) -> str | None:
    """Return the next non-newline character in ``text`` from ``start``."""

    for char in text[start:]:
        if char not in {"\n", "\r"}:
            return char
    return None


def _node_starts_visible_text(node: object) -> bool:
    """Return whether a node should absorb a pending collapsed separator space."""

    macro_name = getattr(node, "macroname", None)
    if macro_name == "\\":
        return False
    return True


def _normalize_leading_label_block(formatted: str) -> tuple[str, bool]:
    """Place a leading ``\\label{...}`` block on its own line above the body."""

    stripped = formatted.lstrip()
    leading_prefix = formatted[: len(formatted) - len(stripped)]
    force_leading_newline = False
    if leading_prefix:
        formatted = stripped

    label_blocks: list[str] = []
    remaining = formatted
    while True:
        stripped_remaining = remaining.lstrip()
        if not stripped_remaining.startswith(r"\label{"):
            break
        label_block = _extract_braced_macro(stripped_remaining, "label")
        if label_block is None:
            break
        label_blocks.append(label_block)
        remaining = stripped_remaining[len(label_block) :]

    if not label_blocks:
        return formatted, force_leading_newline

    body = remaining.lstrip("\n\r ")
    if not leading_prefix:
        force_leading_newline = True
    if not body:
        return "\n".join(label_blocks), force_leading_newline
    return "\n".join([*label_blocks, body]), force_leading_newline


def _finalize_math_body(
    formatted: str,
    *,
    max_width: int,
    normalize_leading_label: bool,
) -> tuple[str, bool]:
    """Normalize labels, collapse source breaks, and wrap long math lines."""

    forced_leading_newline = False
    if normalize_leading_label:
        formatted, forced_leading_newline = _normalize_leading_label_block(formatted)
    formatted = _collapse_nonstructural_line_breaks(formatted)

    final_lines: list[str] = []
    for line in formatted.split("\n"):
        final_lines.extend(_split_long_line(line.rstrip(" \t"), max_width=max_width))
    return "\n".join(final_lines), forced_leading_newline


def _render_nested_environment(node: object, *, max_width: int) -> str:
    """Render a nested helper environment with reformatted body contents."""

    environment_name = _environment_name(node)
    if environment_name is None:
        return node.latex_verbatim()

    pieces = [rf"\begin{{{environment_name}}}"]
    for arg in _node_args(node):
        opening, closing = _argument_delimiters(arg)
        pieces.append(opening)
        pieces.append(
            _render_nodes_to_formatted_string(
                arg.nodelist,
                substack=False,
                start_of_line=False,
                literal_text=False,
                max_width=max_width,
            )
        )
        pieces.append(closing)

    body = _render_nodes_to_formatted_string(
        getattr(node, "nodelist", None),
        substack=False,
        start_of_line=True,
        literal_text=False,
        max_width=max_width,
    )
    finalized_body, _ = _finalize_math_body(
        body,
        max_width=max_width,
        normalize_leading_label=False,
    )
    pieces.extend(["\n", finalized_body, "\n", rf"\end{{{environment_name}}}"])
    return "".join(pieces)


def _collapse_nonstructural_line_breaks(formatted: str) -> str:
    """Collapse source line breaks that are not formatter-significant."""

    lines = formatted.split("\n")
    if len(lines) <= 1:
        return formatted

    collapsed: list[str] = [lines[0].rstrip(" \t")]
    for line in lines[1:]:
        current = line.lstrip(" \t")
        previous = collapsed[-1].strip()
        current_stripped = current.strip()

        if (
            not previous
            or not current_stripped
            or previous.startswith("%")
            or current_stripped.startswith("%")
            or previous.startswith(r"\begin{")
            or previous.startswith(r"\label{")
            or previous in {r"\\", r"\\*"}
            or current_stripped.startswith(r"\end{")
            or current_stripped in {r"\\", r"\\*"}
        ):
            collapsed.append(current.rstrip(" \t"))
            continue

        collapsed[-1] = f"{collapsed[-1].rstrip(' \t')} {current.lstrip(' \t')}".rstrip(" \t")

    return "\n".join(collapsed)


def _extract_braced_macro(text: str, macro_name: str) -> str | None:
    """Return a full braced macro call from the start of ``text``."""

    prefix = rf"\{macro_name}" + "{"
    if not text.startswith(prefix):
        return None

    depth = 0
    for index, char in enumerate(text[len(prefix) - 1 :], start=len(prefix) - 1):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[: index + 1]
    return None


def _split_long_line(line: str, *, max_width: int) -> list[str]:
    """Split a long line at relation symbols, operators, spaces, or width."""

    if len(line) <= max_width:
        return [line]

    aligned_split = _find_aligned_relation_break(line)
    if aligned_split != -1:
        return [line[:aligned_split]] + _split_long_line(line[aligned_split:], max_width=max_width)

    # Increasing allowed depth keeps top-level relations preferred while still
    # giving deeply grouped formulas a usable fallback before hard wrapping.
    for allowed_depth in range(5):
        for symbols in (RELATION_SYMBOLS, OPERATOR_SYMBOLS):
            index = _find_split_index(line, max_width, symbols, allowed_depth)
            if index > 0:
                return [line[:index]] + _split_long_line(line[index:], max_width=max_width)

    # If no preferred operator break exists, still prefer splitting at shallow
    # whitespace before touching spaces inside grouped macro arguments.
    for allowed_depth in range(5):
        space_index = _find_space_split_index(line, max_width, allowed_depth)
        if space_index > 0:
            return [line[:space_index]] + _split_long_line(line[space_index + 1 :], max_width=max_width)

    return [line[:max_width]] + _split_long_line(line[max_width:], max_width=max_width)


def _find_split_index(
    line: str,
    max_width: int,
    symbols: list[str],
    allowed_depth: int,
) -> int:
    """Return the best split point near ``max_width`` for the given symbols."""

    depth_array = _brace_depth_array(line)
    protected_positions = _protected_split_positions(line)
    for symbol in symbols:
        best_before = -1
        first_after = -1
        start = 0
        while True:
            index = line.find(symbol, start)
            if index == -1:
                break
            if symbol.startswith("\\") and _is_embedded_macro_match(line, index, symbol):
                start = index + 1
                continue
            if _split_would_separate_alignment_marker(line, index):
                start = index + 1
                continue
            if index < len(protected_positions) and protected_positions[index]:
                start = index + 1
                continue
            if index < len(depth_array) and depth_array[index] <= allowed_depth:
                if index <= max_width:
                    best_before = max(best_before, index)
                elif first_after == -1 or index < first_after:
                    first_after = index
            start = index + 1
        if best_before != -1:
            return best_before
        if first_after != -1:
            return first_after
    return -1


def _find_space_split_index(line: str, max_width: int, allowed_depth: int) -> int:
    """Return the last eligible space no later than ``max_width`` at a given depth."""

    depth_array = _brace_depth_array(line)
    protected_positions = _protected_split_positions(line)
    best = -1
    for index, char in enumerate(line[:max_width]):
        if char != " ":
            continue
        if index >= len(depth_array) or depth_array[index] > allowed_depth:
            continue
        if index < len(protected_positions) and protected_positions[index]:
            continue
        best = index
    return best


def _brace_depth_array(text: str) -> list[int]:
    """Return brace nesting depth for each character in ``text``."""

    depth_array: list[int] = []
    current_depth = 0
    for char in text:
        if char == "{":
            depth_array.append(current_depth)
            current_depth += 1
        elif char == "}":
            current_depth -= 1
            depth_array.append(current_depth)
        else:
            depth_array.append(current_depth)
    return depth_array


def _split_would_separate_alignment_marker(line: str, index: int) -> bool:
    """Return whether a split at ``index`` would detach an ``&`` from its cell."""

    cursor = index - 1
    while cursor >= 0 and line[cursor] in {" ", "\t"}:
        cursor -= 1
    return cursor >= 0 and line[cursor] == "&"


def _is_embedded_macro_match(line: str, index: int, symbol: str) -> bool:
    """Return whether a macro symbol match is only a prefix inside another macro."""

    if index > 0 and line[index - 1].isalpha():
        return True
    end = index + len(symbol)
    return end < len(line) and line[end].isalpha()


def _protected_split_positions(text: str) -> list[bool]:
    """Return positions that lie inside sub/superscript or macro brace groups."""

    protected = [False] * len(text)
    pending_group_depths: list[int] = []
    group_stack: list[tuple[int, bool]] = []
    depth = 0
    index = 0

    while index < len(text):
        char = text[index]

        if char == "\\":
            index += 1
            while index < len(text) and text[index].isalpha():
                index += 1
            if index < len(text) and text[index] == "*":
                index += 1
            while index < len(text) and text[index] == " ":
                index += 1
            if index < len(text) and text[index] == "{":
                pending_group_depths.append(depth + 1)
            continue

        if char in {"_", "^"}:
            next_index = index + 1
            while next_index < len(text) and text[next_index] == " ":
                next_index += 1
            if next_index < len(text) and text[next_index] == "{":
                pending_group_depths.append(depth + 1)

        if char == "{":
            depth += 1
            is_protected = False
            if pending_group_depths and pending_group_depths[-1] == depth:
                pending_group_depths.pop()
                is_protected = True
            group_stack.append((depth, is_protected))
            index += 1
            continue

        active_protected = any(is_protected for _, is_protected in group_stack)
        if active_protected:
            protected[index] = True

        if char == "}":
            if group_stack and group_stack[-1][0] == depth:
                group_stack.pop()
            depth = max(0, depth - 1)

        index += 1

    return protected


def _find_aligned_relation_break(line: str) -> int:
    """Return an aligned-row break before ``&`` when the row introduces a relation."""

    amp_index = line.find("&")
    if amp_index <= 0:
        return -1

    tail = line[amp_index + 1 :].lstrip(" \t")
    for symbol in RELATION_SYMBOLS:
        if tail.startswith(symbol):
            return amp_index
    return -1


def _node_args(node: object) -> list[object]:
    """Return parsed macro or node arguments across pylatexenc versions."""

    nodeargs = getattr(node, "nodeargs", None)
    if nodeargs is not None:
        return list(nodeargs)

    nodeargd = getattr(node, "nodeargd", None)
    if nodeargd is None:
        return []

    argnlist = getattr(nodeargd, "argnlist", None)
    if argnlist is None:
        return []
    return [arg for arg in argnlist if arg is not None]


def _argument_delimiters(arg: object) -> tuple[str, str]:
    """Return source delimiters for a parsed macro argument."""

    delimiters = getattr(arg, "delimiters", None)
    if delimiters == ("[", "]") or delimiters == ["[", "]"]:
        return "[", "]"
    return "{", "}"


def _environment_name(node: object) -> str | None:
    """Return the environment name recorded by a parsed node."""

    environment_name = getattr(node, "environmentname", None)
    if environment_name is None:
        environment_name = getattr(node, "envname", None)
    return environment_name


def _is_target_math_container(node: object) -> bool:
    """Return whether a parsed node is a top-level math container to rewrite."""

    if _environment_name(node) in MATH_ENVIRONMENTS:
        return True
    return (
        node.__class__.__name__ == "LatexMathNode"
        and getattr(node, "displaytype", None) == "display"
    )


def _container_body_span(node: object) -> tuple[int, int] | None:
    """Return the source span covering only a math container body."""

    nodelist = getattr(node, "nodelist", None)
    if not nodelist:
        return None

    start = getattr(nodelist[0], "pos", None)
    last_node = nodelist[-1]
    last_start = getattr(last_node, "pos", None)
    last_len = getattr(last_node, "len", None)
    if isinstance(start, int) and isinstance(last_start, int) and isinstance(last_len, int):
        return start, last_start + last_len
    return None


def _pylatexenc_install_root() -> Path:
    """Return the user cache directory used for the ``pylatexenc`` install."""

    return Path.home() / ".latex-toolkit" / "pylatexenc"


def _format_process_failure(message: str, completed: subprocess.CompletedProcess[str]) -> str:
    """Return a concise subprocess failure message."""

    details = (completed.stderr or completed.stdout).strip()
    if details:
        return f"{message}: {details}"
    return f"{message} with exit code {completed.returncode}."


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
