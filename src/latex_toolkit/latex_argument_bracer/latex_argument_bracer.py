r"""Make parsed LaTeX arguments and math scripts explicitly braced.

Call ``transform_text(...)`` from Python, or use ``main(...)`` for file,
clipboard, and standard-stream workflows. Complete documents are transformed
only inside their top-level ``document`` environments; input without one is
treated as a fragment.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from collections.abc import Iterable, Sequence
import sys
from pathlib import Path
from typing import Any

from latex_toolkit.lib.dependencies import DependencyManager


# Project shorthand commands that take one mandatory LaTeX argument. Keeping
# their parser specifications together makes additional local macros explicit.
CUSTOM_MACRO_ARGUMENT_SPECS = {
    "FT": "{",
    "mb": "{",
    "mbb": "{",
    "mbf": "{",
    "mc": "{",
    "mf": "{",
    "ms": "{",
}


class ArgumentBracer:
    """Collect source insertions that brace parsed arguments and math scripts.

    Parameters
    ----------
    source : str
        Complete LaTeX source whose parser node positions define every edit.

    Methods
    -------
    transform
        Return source with the requested braces inserted.
    """

    def __init__(self, source: str) -> None:
        self._source = source
        self._insertions: list[tuple[int, int, str]] = []
        self._macro_ends: dict[int, int] = {}

    def transform(self, nodes: Iterable[Any]) -> str:
        """Return source with braces around parsed arguments and math scripts.

        Parameters
        ----------
        nodes : iterable of pylatexenc.latexnodes.nodes.LatexNode
            Parsed nodes in the source scope to transform.

        Returns
        -------
        str
            The original source with non-braced mandatory arguments and math
            script operands enclosed in braces.
        """
        nodes = tuple(nodes)

        # Visit each parser node once so nested arguments contribute edits while
        # shared node references cannot duplicate them.
        visited: set[int] = set()
        for node in nodes:
            self._visit_node(node, visited)

        # Script macros can include their own parsed arguments, so discover
        # their complete spans before wrapping the script operand.
        for node in nodes:
            self._collect_script_braces(node, visited=set())
        return self._apply_insertions()

    def _visit_node(self, node: Any, visited: set[int]) -> None:
        """Collect braces for macro arguments and recursively nested nodes."""
        if id(node) in visited:
            return
        visited.add(id(node))

        if type(node).__name__ == "LatexMacroNode":
            self._macro_ends[node.pos] = node.pos_end
            parsed_arguments = getattr(node, "nodeargd", None)
            arguments = getattr(parsed_arguments, "argnlist", ()) or ()
            argument_specification = getattr(parsed_arguments, "argspec", "") or ""
            for specification, argument in zip(argument_specification, arguments):
                # Optional and star arguments have distinct TeX syntax and are
                # intentionally preserved rather than converted to groups.
                if specification != "{":
                    continue
                if argument is not None and self._needs_braces(argument):
                    self._insertions.extend(
                        (
                            (argument.pos, 1, "{"),
                            (argument.pos_end, 0, "}"),
                        )
                    )

        for argument in getattr(getattr(node, "nodeargd", None), "argnlist", ()) or ():
            if argument is not None:
                self._visit_node(argument, visited)
        for child in getattr(node, "nodelist", ()) or ():
            if child is not None:
                self._visit_node(child, visited)

    def _collect_script_braces(self, node: Any, visited: set[int]) -> None:
        """Collect braces for ungrouped script operands inside math node lists."""
        if id(node) in visited:
            return
        visited.add(id(node))

        if type(node).__name__ == "LatexMathNode":
            content = getattr(node, "nodelist", None)
            if content is not None:
                self._collect_scripts_in_span(content.pos, content.pos_end)

        for argument in getattr(getattr(node, "nodeargd", None), "argnlist", ()) or ():
            if argument is not None:
                self._collect_script_braces(argument, visited)
        for child in getattr(node, "nodelist", ()) or ():
            if child is not None:
                self._collect_script_braces(child, visited)

    def _collect_scripts_in_span(self, start: int, end: int) -> None:
        """Find TeX script tokens in one parser-confirmed math source span."""
        index = start
        while index < end:
            character = self._source[index]
            if character == "\\":
                index = self._control_sequence_end(index, end)
                continue
            if character == "%":
                index = self._comment_end(index, end)
                continue
            if character in "_^":
                argument_start = index + 1
                argument_end = self._script_argument_end(argument_start, end)
                if argument_end is not None:
                    self._insertions.extend(
                        (
                            (argument_start, 0, "{"),
                            (argument_end, 1, "}"),
                        )
                    )
                    index = argument_end
                    continue
            index += 1

    def _script_argument_end(self, start: int, limit: int) -> int | None:
        """Return the end of one ungrouped TeX script argument, if present."""
        if start >= limit or self._source[start] == "{":
            return None
        if self._source[start] == "\\":
            return self._macro_ends.get(start, self._control_sequence_end(start, limit))
        return start + 1

    def _control_sequence_end(self, start: int, limit: int) -> int:
        """Return the source position after a TeX control word or symbol."""
        index = start + 1
        while index < limit and self._source[index].isalpha():
            index += 1
        return index if index > start + 1 else min(start + 2, limit)

    def _comment_end(self, start: int, limit: int) -> int:
        """Return the position after a comment while respecting escaped percent signs."""
        backslashes = 0
        index = start - 1
        while index >= 0 and self._source[index] == "\\":
            backslashes += 1
            index -= 1
        if backslashes % 2:
            return start + 1
        newline = self._source.find("\n", start, limit)
        return limit if newline == -1 else newline + 1

    def _needs_braces(self, argument: Any) -> bool:
        """Return whether a parsed mandatory argument is not already grouped."""
        if argument.pos is None or argument.pos_end is None:
            return False
        return self._source[argument.pos : argument.pos + 1] not in {"{", "["}

    def _apply_insertions(self) -> str:
        """Render collected insertions without changing any original source span."""
        by_position: dict[int, list[tuple[int, str]]] = defaultdict(list)
        for position, priority, text in self._insertions:
            by_position[position].append((priority, text))

        pieces: list[str] = []
        for index, character in enumerate(self._source):
            pieces.extend(text for _, text in sorted(by_position[index]))
            pieces.append(character)
        pieces.extend(text for _, text in sorted(by_position[len(self._source)]))
        return "".join(pieces)


def transform_text(source: str) -> str:
    r"""Make parsed macro arguments and math scripts explicitly braced.

    The parser supplies macro argument boundaries, including ``\frac12`` and
    common alphabet commands such as ``\mathcal A``. Project shorthand macros
    declared in :data:`CUSTOM_MACRO_ARGUMENT_SPECS` use their listed arities.

    Parameters
    ----------
    source : str
        LaTeX source in complete-document or fragment form.

    Returns
    -------
    str
        Source with non-braced mandatory macro arguments and math subscripts
        and superscripts braced.

    Examples
    --------
    Basic usage:

    >>> transform_text(r"$\mathcal A + \frac12 + x_1$")
    '$\\mathcal{A} + \\frac{1}{2} + x_{1}$'
    """
    if not source:
        return source

    RUNTIME_DEPENDENCIES.require("pylatexenc.latexnodes.parsers")
    from pylatexenc.latexnodes.parsers import LatexGeneralNodesParser
    from pylatexenc.latexwalker import LatexWalker, get_default_latex_context_db
    from pylatexenc.macrospec import MacroSpec

    # Supplement the standard macro database with declared project shorthand
    # commands without altering global parser state.
    default_context = get_default_latex_context_db()
    context = default_context.filtered_context(
        keep_categories=default_context.category_list
    )
    context.add_context_category(
        "latex-argument-bracer",
        macros=[
            MacroSpec(name, argument_specification)
            for name, argument_specification in CUSTOM_MACRO_ARGUMENT_SPECS.items()
        ],
        prepend=True,
    )
    nodes, _ = LatexWalker(source, latex_context=context).parse_content(
        LatexGeneralNodesParser()
    )

    # Preserve complete-document preambles while treating standalone material
    # such as a fixture chapter as a useful transformable fragment.
    document_bodies = [
        node.nodelist
        for node in nodes
        if type(node).__name__ == "LatexEnvironmentNode"
        and node.environmentname == "document"
    ]
    if not document_bodies:
        return ArgumentBracer(source).transform(nodes)

    return ArgumentBracer(source).transform(
        node for body in document_bodies for node in body
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Run the argument bracer in file, clipboard, or standard-stream mode.

    With no arguments, the command transforms the system clipboard.

    Parameters
    ----------
    argv : sequence of str, optional
        Command-line arguments without the executable name.

    Returns
    -------
    int
        Zero after a completed transformation.
    """
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.input_file is None and not args.clipboard and not args.stdin:
        args.clipboard = True
    selected_inputs = sum((args.input_file is not None, args.clipboard, args.stdin))
    if selected_inputs != 1:
        parser.error("provide an input file, --clipboard, or --stdin")
    if (args.clipboard or args.stdin) and args.output_file is not None:
        parser.error("--output cannot be used with --clipboard or --stdin")

    if args.clipboard:
        _process_clipboard()
    elif args.stdin:
        sys.stdout.write(transform_text(sys.stdin.read()))
    else:
        output_path = args.output_file or _default_output_path(args.input_file)
        _process_file(args.input_file, output_path)
        print(f"Transformed file written to: {output_path}")
    return 0


RUNTIME_DEPENDENCIES = DependencyManager(
    {
        "pylatexenc.latexnodes.parsers": "pylatexenc>=3.0a33",
        "pyperclip": "pyperclip>=1.9",
    }
)


def _build_parser() -> argparse.ArgumentParser:
    """Build the argument-bracing command-line interface."""
    parser = argparse.ArgumentParser(
        description="Brace parsed LaTeX macro arguments and math scripts."
    )
    parser.add_argument("input_file", nargs="?", type=Path, help="UTF-8 LaTeX file")
    parser.add_argument("-o", "--output", "--output-file", dest="output_file", type=Path)
    parser.add_argument("--clipboard", action="store_true")
    parser.add_argument("--stdin", action="store_true")
    return parser


def _default_output_path(input_path: Path) -> Path:
    """Return a sibling output path with ``_braced`` before the extension."""
    suffix = input_path.suffix or ".tex"
    stem = input_path.stem if input_path.suffix else input_path.name
    return input_path.with_name(f"{stem}_braced{suffix}")


def _process_file(input_path: Path, output_path: Path) -> Path:
    """Transform one UTF-8 source file and write the separate result."""
    source = input_path.read_text(encoding="utf-8")
    output_path.write_text(transform_text(source), encoding="utf-8")
    return output_path


def _process_clipboard() -> None:
    """Transform nonempty clipboard text and copy the result back."""
    pyperclip = RUNTIME_DEPENDENCIES.require("pyperclip")
    source = pyperclip.paste()
    if not source.strip():
        print("Clipboard is empty; nothing was changed.")
        return
    pyperclip.copy(transform_text(source))
    print("Transformed LaTeX written back to the clipboard.")
