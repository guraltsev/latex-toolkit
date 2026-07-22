# latex_transformer_template

Provide a small, customizable LaTeX syntax-tree transformation template. Its
example changes `\emph` to `\textbf` inside top-level document bodies.

## Usage

```powershell
python -m latex_toolkit.latex_transformer_template .\paper.tex
python -m latex_toolkit.latex_transformer_template .\paper.tex -o .\paper.out.tex
python -m latex_toolkit.latex_transformer_template --clipboard
Get-Content .\paper.tex -Raw | python -m latex_toolkit.latex_transformer_template --stdin
```

Without an output path, file mode writes `paper_modified.tex` beside the
source. Clipboard mode replaces nonempty clipboard text. Standard-stream mode
reads stdin and writes only the transformed text to stdout. Neither mode can be
combined with a file or output path.

## Python API

`transform_text(source)` performs the example transformation. Customize
`DocumentTransformer` to define another node transformation.
