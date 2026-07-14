r"""Transform LaTeX document bodies through a small syntax-tree visitor.

Call ``transform_text(...)`` from Python, or use ``main(...)`` for file and
clipboard workflows. The included example changes ``\emph`` to ``\textbf``
inside the ``document`` environment while leaving the preamble unchanged.
"""

from __future__ import annotations

import argparse
import importlib
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pylatexenc.latexnodes.nodes import LatexMacroNode


# Public workflows


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
    latex_walker, environment_type, recomposer_type = _latex_api()

    # Parse the complete source so the renderer can preserve the preamble and
    # every document delimiter alongside the transformed body.
    walker = latex_walker(source)
    nodes, _, _ = walker.get_latex_nodes()

    # Enter only top-level document environments. Starting traversal at their
    # children keeps package setup and command definitions unchanged.
    transformer = DocumentTransformer()
    for node in nodes:
        if (
            isinstance(node, environment_type)
            and node.environmentname == "document"
        ):
            transformer.transform(node.nodelist)

    return recomposer_type().latex_recompose(nodes)


def process_file(input_path: Path, output_path: Path) -> Path:
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


def main(argv: Sequence[str] | None = None) -> int:
    """Run the transformer in explicit file or clipboard mode.

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
        Arguments do not select exactly one input mode, or combine clipboard
        mode with an output path.
    """
    parser = _build_parser()
    args = parser.parse_args(argv)

    # Require an explicit input mode so invoking the command accidentally does
    # not read from or replace the user's clipboard.
    if bool(args.input_file) == args.clipboard:
        parser.error("provide an input file or --clipboard, but not both")
    if args.clipboard and args.output_file is not None:
        parser.error("--output cannot be used with --clipboard")

    if args.clipboard:
        _transform_clipboard()
        return 0

    input_path = args.input_file
    output_path = args.output_file or _default_output_path(input_path)
    process_file(input_path, output_path)
    print(f"Transformed file written to: {output_path}")
    return 0


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


class DependencyManager:
    """Load configured modules and install their distributions when necessary.

    Parameters
    ----------
    distributions : dict of str to str
        Import names mapped to requirement strings accepted by ``pip``.

    Methods
    -------
    require
        Import a module, installing and re-importing it when absent.

    Attributes
    ----------
    distributions : dict of str to str
        An independent copy of the import-to-requirement mapping.

    Examples
    --------
    Loading an available module does not invoke ``pip``:

    >>> manager = DependencyManager({"json": "json"})
    >>> manager.require("json").loads('{"ready": true}')
    {'ready': True}
    """

    def __init__(self, distributions: dict[str, str]) -> None:
        self.distributions = dict(distributions)

    def require(self, import_name: str) -> ModuleType:
        """Import a configured module, installing and re-importing it if absent.

        Parameters
        ----------
        import_name : str
            Top-level module name configured when the manager was constructed.

        Returns
        -------
        types.ModuleType
            The imported module object.

        Raises
        ------
        KeyError
            The requested module was not configured for this manager.
        ModuleNotFoundError
            An installed module is missing one of its own dependencies.
        subprocess.CalledProcessError
            ``pip`` could not install the configured distribution.
        """
        requirement = self.distributions[import_name]

        # Only absence of the requested top-level module triggers installation.
        # Errors raised from inside an installed package must remain visible.
        try:
            return importlib.import_module(import_name)
        except ModuleNotFoundError as error:
            if error.name != import_name:
                raise

        # Install into the active interpreter, then clear every partial import
        # entry before loading the new package into the current process.
        print(f"{import_name} is not installed; installing {requirement}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", requirement])
        importlib.invalidate_caches()
        for module_name in tuple(sys.modules):
            if module_name == import_name or module_name.startswith(
                f"{import_name}."
            ):
                sys.modules.pop(module_name, None)

        module = importlib.import_module(import_name)
        print(f"Installed and imported {import_name}.")
        return module


RUNTIME_DEPENDENCIES = DependencyManager(
    {
        "pylatexenc": "pylatexenc>=3.0a33",
        "pyperclip": "pyperclip>=1.9",
    }
)


def _latex_api() -> tuple[type[Any], type[Any], type[Any]]:
    """Load the parser, document-node, and renderer classes on demand."""
    RUNTIME_DEPENDENCIES.require("pylatexenc")

    from pylatexenc.latexnodes import LatexNodesLatexRecomposer
    from pylatexenc.latexnodes.nodes import LatexEnvironmentNode
    from pylatexenc.latexwalker import LatexWalker

    return LatexWalker, LatexEnvironmentNode, LatexNodesLatexRecomposer


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
        help="destination path (default: INPUT_modified.tex)",
    )
    parser.add_argument(
        "--clipboard",
        action="store_true",
        help="transform the system clipboard instead of a file",
    )
    return parser


def _default_output_path(input_path: Path) -> Path:
    """Return a sibling output path with ``_modified`` before the extension."""
    suffix = input_path.suffix or ".tex"
    stem = input_path.stem if input_path.suffix else input_path.name
    return input_path.with_name(f"{stem}_modified{suffix}")


def _transform_clipboard() -> None:
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
