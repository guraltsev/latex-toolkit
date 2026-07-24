r"""This module transforms LaTeX document bodies through a small syntax-tree visitor.

The ``transform_text(...)`` API supports Python callers, and ``main(...)`` supports
clipboard, and standard-stream workflows. The included example changes
``\emph`` to ``\textbf`` inside the ``document`` environment while leaving the
preamble unchanged.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any
from typing import TYPE_CHECKING

from latex_toolkit.lib.dependencies import DependencyManager
from latex_toolkit.lib.backup import backup_file

if TYPE_CHECKING:
    from pylatexenc.latexnodes.nodes import LatexMacroNode


class DocumentTransformer:
    r"""Apply customizable edits within a parsed document environment.

    Add methods named after pylatexenc node classes, such as
    ``visit_LatexEnvironmentNode``, to define other transformations. Traversal
    begins at a document environment's children, so this class does not need to
    distinguish body nodes from preamble nodes.

    Methods
    -------
    transform
        Traverse parsed nodes and apply matching visitor methods.
    visit_LatexMacroNode
        Replace ``\emph`` macro names with ``\textbf``.
    """

    def transform(self, nodes: Any) -> None:
        """Apply visitor methods recursively to a parsed LaTeX node list.

        Parameters
        ----------
        nodes : pylatexenc.latexnodes.nodes.LatexNodeList
            Parsed nodes belonging to a LaTeX document body.
        """
        for node in nodes:
            self._visit_node(node)

    def visit_LatexMacroNode(self, node: LatexMacroNode) -> None:
        r"""Replace an ``\emph`` macro name with ``\textbf``."""
        # This branch is the example transformation. Replace it with the macro
        # rule needed by the derived command, or add other visitor methods.
        if node.macroname == "emph":
            node.macroname = "textbf"

    def _visit_node(self, node: Any) -> None:
        """Apply a matching visitor method and descend into child nodes."""
        # A node class maps directly to its optional visitor method.
        visitor = getattr(self, f"visit_{type(node).__name__}", None)
        if visitor is not None:
            visitor(node)

        # Macro and environment arguments are separate from body node lists.
        parsed_arguments = getattr(node, "nodeargd", None)
        for argument in getattr(parsed_arguments, "argnlist", ()) or ():
            if argument is not None:
                self._visit_node(argument)

        # Groups, math nodes, and environments expose nested content here.
        for child in getattr(node, "nodelist", ()) or ():
            if child is not None:
                self._visit_node(child)


# Auxiliary implementation
# ------------------------


def transform_text(source: str) -> str:
    r"""Apply the example node transformation to a LaTeX document body.

    Text outside a ``document`` environment is preserved. To customize the
    transformation, edit or extend :class:`DocumentTransformer`.

    Parameters
    ----------
    source : str
        LaTeX source to parse and transform.

    Returns
    -------
    str
        Rendered LaTeX with matching nodes transformed in each top-level
        ``document`` environment.

    Examples
    --------
    Basic usage:

    >>> source = r"\begin{document}\emph{Important}\end{document}"
    >>> transform_text(source)
    '\\begin{document}\\textbf{Important}\\end{document}'
    """

    RUNTIME_DEPENDENCIES.require("pylatexenc.latexnodes.parsers")
    from pylatexenc.latexnodes import LatexNodesLatexRecomposer
    from pylatexenc.latexnodes.nodes import LatexEnvironmentNode
    from pylatexenc.latexnodes.parsers import LatexGeneralNodesParser
    from pylatexenc.latexwalker import LatexWalker

    # Parse the complete source so the renderer can preserve the preamble and
    # every document delimiter alongside the transformed body.
    nodes, _ = LatexWalker(source).parse_content(LatexGeneralNodesParser())

    # Enter only top-level document environments. Starting traversal at their
    # children keeps package setup and command definitions unchanged.
    transformer = DocumentTransformer()
    for node in nodes:
        if (
            isinstance(node, LatexEnvironmentNode)
            and node.environmentname == "document"
        ):
            transformer.transform(node.nodelist)

    return LatexNodesLatexRecomposer().latex_recompose(nodes)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the transformer in file, clipboard, or standard-stream mode.

    With no arguments, the command transforms the system clipboard.

    Parameters
    ----------
    argv : sequence of str, optional
        Command-line arguments without the executable name. When omitted,
        arguments are read from ``sys.argv``.

    Returns
    -------
    int
        Process exit status; zero indicates a completed transformation.

    Raises
    ------
    SystemExit
        Arguments select multiple input modes or combine a non-file mode with
        an output path.
    """
    parser = _build_parser()
    args = parser.parse_args(argv)

    # Default to clipboard mode when the caller does not provide an input file
    # or an explicit mode flag.
    if args.input_file is None and not args.clipboard and not args.stdin:
        args.clipboard = True

    # Reject ambiguous input modes before performing any transformation.
    selected_inputs = sum((args.input_file is not None, args.clipboard, args.stdin))
    if selected_inputs != 1:
        parser.error("provide an input file, --clipboard, or --stdin")
    if (args.clipboard or args.stdin) and args.output_file is not None:
        parser.error("--output cannot be used with --clipboard or --stdin")

    # Handle the validated input modes as explicit cases before returning
    # one shared success status.
    if args.clipboard:
        _process_clipboard()
    elif args.stdin:
        sys.stdout.write(transform_text(sys.stdin.read()))
    else:
        input_path = args.input_file
        if args.output_file is None and not args.no_backup:
            backup_file(input_path)
        output_path = args.output_file or input_path
        _process_file(input_path, output_path)
        print(f"Transformed file written to: {output_path}")

    return 0


# Keep only the template's dependency declarations at its command boundary.
RUNTIME_DEPENDENCIES = DependencyManager(
    {
        "pylatexenc.latexnodes.parsers": "pylatexenc>=3.0a33",
        "pyperclip": "pyperclip>=1.9",
    }
)

def _build_parser() -> argparse.ArgumentParser:
    """Build the command-line interface shared by direct and module execution."""
    parser = argparse.ArgumentParser(
        description=(
            r"Transform LaTeX inside \begin{document} ... \end{document}."
        )
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        type=Path,
        help="UTF-8 LaTeX file to transform",
    )
    parser.add_argument(
        "-o",
        "--output",
        "--output-file",
        dest="output_file",
        type=Path,
        help="destination path; preserves INPUT and skips its backup",
    )
    parser.add_argument(
        "-B", "--no-backup", action="store_true", help="overwrite INPUT without a backup"
    )
    parser.add_argument(
        "--clipboard",
        action="store_true",
        help="transform the system clipboard instead of a file",
    )
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="read UTF-8 LaTeX from stdin and write the result to stdout",
    )
    return parser


def _default_output_path(input_path: Path) -> Path:
    """Return a sibling output path with ``_modified`` before the extension."""
    suffix = input_path.suffix or ".tex"
    stem = input_path.stem if input_path.suffix else input_path.name
    return input_path.with_name(f"{stem}_modified{suffix}")


def _process_file(input_path: Path, output_path: Path) -> Path:
    """Transform one UTF-8 LaTeX file and write a separate UTF-8 result.

    Parameters
    ----------
    input_path : pathlib.Path
        Source file to read without modifying.
    output_path : pathlib.Path
        Destination to create or replace with the transformed source.

    Returns
    -------
    pathlib.Path
        The destination path supplied by the caller.

    Raises
    ------
    OSError
        The source cannot be read or the destination cannot be written.
    """
    # Read before opening the destination so an identical input and output path
    # cannot truncate the source before transformation completes.
    source = input_path.read_text(encoding="utf-8")
    transformed = transform_text(source)
    output_path.write_text(transformed, encoding="utf-8")
    return output_path


def _process_clipboard() -> None:
    """Transform nonempty clipboard text and copy the result back."""
    # Delay clipboard installation and import until the user selects that
    # boundary; ordinary text and file transformations do not need it.
    pyperclip = RUNTIME_DEPENDENCIES.require("pyperclip")

    source = pyperclip.paste()
    if not source.strip():
        print("Clipboard is empty; nothing was changed.")
        return

    transformed = transform_text(source)
    pyperclip.copy(transformed)
    print("Transformed LaTeX written back to the clipboard.")


if __name__ == "__main__":
    raise SystemExit(main())
