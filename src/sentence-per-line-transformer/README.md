# LaTeX transformer template

A small, production-shaped starting point for syntax-aware LaTeX rewrites.
It parses source with `pylatexenc`, applies visitor methods only inside the
top-level `document` environment, and renders the complete source again.

The included example rewrites `\emph{...}` as `\textbf{...}`. It is meant to
be replaced with the rules for your own command.

## What the template provides

- A focused `DocumentTransformer` visitor with an obvious customization point.
- A `DependencyManager` that owns fallback installation and re-imports.
- File mode that preserves the input and writes a separate output file.
- Explicit clipboard mode that never runs merely because an input was omitted.
- A public `transform_text()` API for composition and testing.
- Installable `python -m` and console-script entry points.
- UTF-8 file I/O and comments preserved by the LaTeX renderer.

## Requirements and installation

Python 3.11 or newer is required. Create a virtual environment and install the
project in editable mode from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --editable .
```

Dependencies are declared in `pyproject.toml`, so a normal project install
fetches them up front. When the template is run directly from a source checkout,
`DependencyManager` imports each dependency, installs it with the active
interpreter's `pip` only when it is absent, invalidates import caches, and
re-imports it into the current process. Clipboard support remains lazily loaded
until `--clipboard` is selected.

## Usage

Transform a file and let the command choose a sibling output path:

```powershell
python -m latex_transformer_template .\paper.tex
# Writes .\paper_modified.tex
```

Choose the output path explicitly:

```powershell
python -m latex_transformer_template .\paper.tex -o .\revised.tex
```

After installation, the equivalent console command is:

```powershell
latex-transformer .\paper.tex --output .\revised.tex
```

Clipboard access is always explicit:

```powershell
python -m latex_transformer_template --clipboard
```

File mode never overwrites the input. Clipboard mode rejects input and output
paths, and an empty clipboard is left unchanged.

## Example

Given this source:

```latex
\newcommand{\term}[1]{\emph{#1}}

\begin{document}
An \emph{important} result.
\end{document}
```

the example transform produces:

```latex
\newcommand{\term}[1]{\emph{#1}}

\begin{document}
An \textbf{important} result.
\end{document}
```

The preamble remains unchanged because traversal starts inside `document`.

## Customize the transformation

Edit `DocumentTransformer` in
`src/latex_transformer_template/latex_transformer_template.py`. The example
macro rule is deliberately small:

```python
def visit_LatexMacroNode(self, node: LatexMacroNode) -> None:
    if node.macroname == "emph":
        node.macroname = "textbf"
```

Add methods such as `visit_LatexEnvironmentNode` for the other node types your
transform needs. The template dispatches each node to its matching method, then
descends into macro arguments and nested content.

The `pylatexenc` parser represents LaTeX syntax, not TeX execution. A visitor
can inspect and rewrite parsed commands and environments, but it does not
expand user macros or reproduce the behavior of a TeX engine.

## Dependency bootstrapping

The dependency manager, mapping, parser loader, CLI helpers, and clipboard
boundary all live in the clearly marked auxiliary section at the end of the
single template file:

```python
RUNTIME_DEPENDENCIES = DependencyManager(
    {
        "pylatexenc": "pylatexenc>=3.0a33",
        "pyperclip": "pyperclip>=1.9",
    }
)
```

Add a package there when a derived transformer needs another runtime module,
then call `RUNTIME_DEPENDENCIES.require("import_name")` at the boundary that
first uses it. A missing top-level module is installed and re-imported. An import
failure caused by one of an already installed package's own missing imports is
allowed to surface instead of being misdiagnosed as an absent package.

## Python API

Use `transform_text()` when another program owns I/O:

```python
from latex_transformer_template import transform_text

source = r"\begin{document}\emph{Important}\end{document}"
result = transform_text(source)
print(result)
```

Use `process_file(input_path, output_path)` with `pathlib.Path` objects for the
same UTF-8 file behavior as the CLI.

## Development

Install test tooling and run the observable behavior tests:

```powershell
python -m pip install --editable . pytest
python -m pytest
```

Repository-wide authoring rules live under `docs/`; `AGENTS.md` links to the
applicable testing, docstring, Python style, and architecture guidance.
