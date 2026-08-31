r"""Convert recognized Unicode math symbols in LaTeX math to LaTeX macros.

The ``transform_text(...)`` API accepts fragments or complete documents, and
``main(...)`` supports file, clipboard, and standard-stream workflows. Only parsed
math delimiters and common math environments are changed.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from latex_toolkit.lib.backup import backup_file
from latex_toolkit.lib.dependencies import DependencyManager
from latex_toolkit.lib.streams import configure_utf8_standard_streams


# Unicode input uses one canonical LaTeX spelling for each recognized symbol.
# The two epsilon glyphs retain distinct macros to preserve their appearance.
UNICODE_TO_LATEX = {
    "α": r"\alpha", "β": r"\beta", "γ": r"\gamma", "δ": r"\delta",
    "ε": r"\epsilon", "ζ": r"\zeta", "η": r"\eta", "θ": r"\theta",
    "ι": r"\iota", "κ": r"\kappa", "λ": r"\lambda", "μ": r"\mu", "ν": r"\nu",
    "ξ": r"\xi", "π": r"\pi", "ρ": r"\rho", "σ": r"\sigma", "τ": r"\tau",
    "υ": r"\upsilon", "φ": r"\phi", "χ": r"\chi", "ψ": r"\psi", "ω": r"\omega",
    "ϵ": r"\varepsilon", "ϑ": r"\vartheta", "ϖ": r"\varpi", "ϱ": r"\varrho",
    "ς": r"\varsigma", "ϕ": r"\varphi", "ϰ": r"\varkappa", "Γ": r"\Gamma",
    "Δ": r"\Delta", "Θ": r"\Theta", "Λ": r"\Lambda", "Ξ": r"\Xi", "Π": r"\Pi",
    "Σ": r"\Sigma", "Υ": r"\Upsilon", "Φ": r"\Phi", "Ψ": r"\Psi", "Ω": r"\Omega",
    "∅": r"\emptyset", "∖": r"\setminus", "≤": r"\leq", "∧": r"\wedge",
    "→": r"\to",
}

# LaTeX input accepts conventional aliases even though Unicode input emits a
# single canonical spelling. This direction is intentionally many-to-one.
LATEX_TO_UNICODE = {
    latex_macro.removeprefix("\\"): symbol
    for symbol, latex_macro in UNICODE_TO_LATEX.items()
}
LATEX_TO_UNICODE.update(
    {
        "varnothing": "∅",
        "smallsetminus": "∖",
        "le": "≤",
        "land": "∧",
        "rightarrow": "→",
    }
)

# Environments whose contents LaTeX typesets in math mode.
MATH_ENVIRONMENTS = frozenset(
    {
        "math",
        "displaymath",
        "equation",
        "equation*",
        "eqnarray",
        "eqnarray*",
        "align",
        "align*",
        "alignat",
        "alignat*",
        "aligned",
        "alignedat",
        "gather",
        "gather*",
        "gathered",
        "multline",
        "multline*",
        "flalign",
        "flalign*",
        "split",
        "cases",
        "matrix",
        "pmatrix",
        "bmatrix",
        "Bmatrix",
        "vmatrix", "Vmatrix", "smallmatrix",
    }
)


def transform_text(source: str, *, reverse: bool = False) -> str:
    r"""Convert recognized math symbols only where LaTeX is in math mode.

    Set ``reverse`` to turn recognized control words, including supported
    aliases, back into their Unicode symbols. Complete documents retain their
    preambles verbatim; fragments are transformed throughout.

    Parameters
    ----------
    source : str
        LaTeX source in complete-document or fragment form.
    reverse : bool, optional
        Convert recognized math macros to Unicode when true.

    Returns
    -------
    str
        Source with recognized math notation converted in math mode only.

    Examples
    --------
    Basic usage:

    >>> transform_text("Text α; math $α + Ω$.")
    'Text α; math $\\alpha + \\Omega$.'
    """
    if not source:
        return source

    nodes = _parse(source)

    # Preserve complete-document preambles while accepting standalone snippets.
    document_bodies = [
        node.nodelist
        for node in nodes
        if type(node).__name__ == "LatexEnvironmentNode"
        and node.environmentname == "document"
    ]
    scopes = document_bodies or [nodes]

    # Collect parser-confirmed source edits so comments and prose remain intact.
    edits: list[tuple[int, int, str]] = []
    for scope in scopes:
        _collect_math_edits(source, scope, reverse=reverse, in_math=False, edits=edits)
    return _apply_edits(source, edits)


def main(argv: Sequence[str] | None = None) -> int:
    """Run Unicode symbol to LaTeX conversion in a selected input mode.

    Parameters
    ----------
    argv : sequence of str, optional
        Command-line arguments without the executable name.

    Returns
    -------
    int
        Zero after a completed transformation.

    Raises
    ------
    SystemExit
        Arguments select incompatible input or output modes.
    """
    return _run_command(argv, reverse=False)


def _parse(source: str) -> Any:
    """Parse source into nodes whose spans define safe edits."""
    RUNTIME_DEPENDENCIES.require("pylatexenc.latexnodes.parsers")
    from pylatexenc.latexnodes.parsers import LatexGeneralNodesParser
    from pylatexenc.latexwalker import LatexWalker

    nodes, _ = LatexWalker(source).parse_content(LatexGeneralNodesParser())
    return nodes


def _collect_math_edits(
    source: str,
    nodes: Any,
    *,
    reverse: bool,
    in_math: bool,
    edits: list[tuple[int, int, str]],
) -> None:
    """Collect recognized symbol replacements from parser nodes in math scope."""
    for node in nodes:
        node_type = type(node).__name__
        node_in_math = (
            in_math
            or node_type == "LatexMathNode"
            or (
                node_type == "LatexEnvironmentNode"
                and getattr(node, "environmentname", None) in MATH_ENVIRONMENTS
            )
        )

        # Character nodes exclude comments and control sequences, making their
        # positions safe places to replace Unicode characters directly.
        if node_in_math and node_type == "LatexCharsNode" and not reverse:
            original = source[node.pos : node.pos_end]
            converted = original.translate(str.maketrans(UNICODE_TO_LATEX))
            if converted != original:
                edits.append((node.pos, node.pos_end, converted))

        # Macro names are parsed separately, so longer similarly named control
        # words such as ``\alphabeta`` cannot be mistaken for ``\alpha``.
        if node_in_math and node_type == "LatexMacroNode" and reverse:
            macro_name = getattr(node, "macroname", "")
            unicode_symbol = LATEX_TO_UNICODE.get(macro_name)
            if unicode_symbol is not None:
                end = node.pos + len(macro_name) + 1
                edits.append((node.pos, end, unicode_symbol))

        children = getattr(node, "nodelist", ()) or ()
        _collect_math_edits(
            source, children, reverse=reverse, in_math=node_in_math, edits=edits
        )
        arguments = getattr(getattr(node, "nodeargd", None), "argnlist", ()) or ()
        for argument in arguments:
            if argument is not None:
                _collect_math_edits(
                    source,
                    (argument,),
                    reverse=reverse,
                    in_math=node_in_math,
                    edits=edits,
                )


def _apply_edits(source: str, edits: list[tuple[int, int, str]]) -> str:
    """Apply non-overlapping source edits from right to left."""
    for start, end, replacement in sorted(set(edits), reverse=True):
        source = source[:start] + replacement + source[end:]
    return source


# Keep parser and clipboard installation at the command boundary so text-only
# callers do not import optional runtime modules eagerly.
RUNTIME_DEPENDENCIES = DependencyManager(
    {
        "pylatexenc.latexnodes.parsers": "pylatexenc>=3.0a33",
        "pyperclip": "pyperclip>=1.9",
    }
)


def _run_command(argv: Sequence[str] | None, *, reverse: bool) -> int:
    """Run one conversion direction in file, clipboard, or stream mode."""
    parser = _build_parser(reverse)
    args = parser.parse_args(argv)
    if args.input_file is None and not args.clipboard and not args.stdin:
        args.clipboard = True
    selected_inputs = sum((args.input_file is not None, args.clipboard, args.stdin))
    if selected_inputs != 1:
        parser.error("provide an input file, --clipboard, or --stdin")
    if (args.clipboard or args.stdin) and args.output_file is not None:
        parser.error("--output cannot be used with --clipboard or --stdin")

    if args.clipboard:
        _transform_clipboard(reverse)
    elif args.stdin:
        configure_utf8_standard_streams()
        sys.stdout.write(transform_text(sys.stdin.read(), reverse=reverse))
    else:
        if args.output_file is None and not args.no_backup:
            backup_file(args.input_file)
        output_path = args.output_file or args.input_file
        _process_file(args.input_file, output_path, reverse=reverse)
        print(f"Transformed file written to: {output_path}")
    return 0


def _build_parser(reverse: bool) -> argparse.ArgumentParser:
    """Build the command-line parser for one conversion direction."""
    direction = (
        "recognized LaTeX math macros to Unicode symbols"
        if reverse
        else "recognized Unicode math symbols to LaTeX macros"
    )
    parser = argparse.ArgumentParser(description=f"Convert {direction} in math mode.")
    parser.add_argument("input_file", nargs="?", type=Path, help="UTF-8 LaTeX file")
    parser.add_argument("-o", "--output", "--output-file", dest="output_file", type=Path)
    parser.add_argument("-B", "--no-backup", action="store_true")
    parser.add_argument("--clipboard", action="store_true")
    parser.add_argument("--stdin", action="store_true")
    return parser


def _process_file(input_path: Path, output_path: Path, *, reverse: bool) -> Path:
    """Transform a UTF-8 LaTeX file without reading a truncated source."""
    source = input_path.read_text(encoding="utf-8")
    output_path.write_text(transform_text(source, reverse=reverse), encoding="utf-8")
    return output_path


def _transform_clipboard(reverse: bool) -> None:
    """Transform nonempty clipboard source and return it to the clipboard."""
    pyperclip = RUNTIME_DEPENDENCIES.require("pyperclip")
    source = pyperclip.paste()
    if not source.strip():
        print("Clipboard is empty; nothing was changed.")
        return
    pyperclip.copy(transform_text(source, reverse=reverse))
    print("Converted LaTeX written back to the clipboard.")
