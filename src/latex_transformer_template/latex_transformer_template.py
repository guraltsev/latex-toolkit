import sys
import subprocess
import argparse

def ensure_pylatexenc():
    """Install pylatexenc if not already available."""
    try:
        import pylatexenc  # noqa: F401
    except ImportError:
        print("pylatexenc not found. Installing...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pylatexenc'])
        print("Installation complete.")

def ensure_pyperclip():
    """Install pyperclip if not already available."""
    try:
        import pyperclip  # noqa: F401
    except ImportError:
        print("pyperclip not found. Installing...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyperclip'])
        print("Installation complete.")

def transform_latex_string(source: str) -> str:
    """
    Parse the LaTeX source, transform nodes inside the document environment,
    and return the modified source string.
    """
    # Import pylatexenc only after it's guaranteed to be installed
    from pylatexenc.latexwalker import LatexWalker
    from pylatexenc.latexnodes import LatexEnvironmentNode, LatexMacroNode
    from pylatexenc.latexnodes.visitor import LatexNodeVisitor
    from pylatexenc.latexnodes.printer import LatexNodesPrinter

    class DocumentTransformer(LatexNodeVisitor):
        """Visitor that applies custom transformations inside the document environment."""
        def __init__(self, context=None):
            super().__init__(context)
            self.printer = LatexNodesPrinter(keep_comments=True)

        def visit_environment(self, node: LatexEnvironmentNode):
            if node.environmentname == 'document':
                self.visit_children(node)
            else:
                self.visit_children(node)   # change if you want to skip others

        def visit_macro(self, node: LatexMacroNode):
            """Example: replace \emph{...} with \textbf{...}"""
            if node.macroname == 'emph':
                node.macroname = 'textbf'
            self.visit_children(node)

        # Add other visit_* methods as needed

    walker = LatexWalker(source)
    nodes, _, _ = walker.get_latex_nodes()

    transformer = DocumentTransformer()
    for node in nodes:
        transformer.visit(node)

    printer = LatexNodesPrinter(keep_comments=True)
    return printer.print_node_list(nodes)

def process_latex_file(input_path: str, output_path: str) -> None:
    """Read a LaTeX file, transform it, and write the result."""
    with open(input_path, 'r', encoding='utf-8') as f:
        source = f.read()
    modified = transform_latex_string(source)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(modified)
    print(f"Transformed file written to: {output_path}")

def clipboard_convert():
    """Get LaTeX from clipboard, transform it, and put result back."""
    import pyperclip   # safe because ensure_pyperclip() was called
    source = pyperclip.paste()
    if not source or not source.strip():
        print("Clipboard is empty. Nothing to do.")
        return
    print("Read LaTeX from clipboard. Transforming...")
    modified = transform_latex_string(source)
    pyperclip.copy(modified)
    print("Transformed LaTeX written back to clipboard.")

def main():
    # First, ensure both libraries are available
    ensure_pylatexenc()
    ensure_pyperclip()

    parser = argparse.ArgumentParser(
        description="Transform LaTeX files (only inside \\begin{document}...\\end{document})"
    )
    parser.add_argument('input_file', nargs='?', help='Input LaTeX file')
    parser.add_argument('output_file', nargs='?', help='Output file (if input given)')

    args = parser.parse_args()

    if args.input_file:
        # File mode
        if not args.output_file:
            # Generate output filename by inserting "_modified" before extension
            if '.' in args.input_file:
                base, ext = args.input_file.rsplit('.', 1)
                output_file = f"{base}_modified.{ext}"
            else:
                output_file = args.input_file + "_modified.tex"
        else:
            output_file = args.output_file
        process_latex_file(args.input_file, output_file)
    else:
        # Clipboard mode
        clipboard_convert()

if __name__ == '__main__':
    main()