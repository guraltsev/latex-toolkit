# template

Provide a small, customizable parser-based LaTeX transformation template. The
included example traverses every node in each top-level `document` body and
renames the `\emph` macro to `\textbf`, including occurrences nested in macro
arguments, groups, math, and environments. The LaTeX is then recomposed from
the modified syntax tree.

Text outside `document` environments, including the preamble, is preserved.
Unlike the other transformation commands, this template operates only on
complete document bodies; it is intended to be edited by extending
`DocumentTransformer` with node-specific visitor methods.

## Usage

```powershell
python -m latex_toolkit.template .\paper.tex
python -m latex_toolkit.template .\paper.tex -o .\paper.out.tex
python -m latex_toolkit.template --clipboard
Get-Content .\paper.tex -Raw | python -m latex_toolkit.template --stdin
```

Without an output path, file mode writes `paper_modified.tex` beside the
source. Clipboard mode replaces nonempty clipboard text. Standard-stream mode
reads stdin and writes only the transformed text to stdout. Neither mode can be
combined with a file or output path.

## Python API

`transform_text(source)` performs the example transformation. Customize
`DocumentTransformer` to define another node transformation.
