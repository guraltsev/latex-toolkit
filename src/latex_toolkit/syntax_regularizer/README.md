# syntax_regularizer

Regularize LaTeX source layout while preserving protected math, table, and
verbatim-like content.

## Usage

```powershell
python -m latex_toolkit.syntax_regularizer .\paper.tex
python -m latex_toolkit.syntax_regularizer .\paper.tex -o .\paper.out.tex
python -m latex_toolkit.syntax_regularizer --clipboard
Get-Content .\paper.tex -Raw | python -m latex_toolkit.syntax_regularizer --stdin
```

Without an output path, file mode writes `paper_regularized.tex` beside the
source. Clipboard mode replaces nonempty clipboard text. Standard-stream mode
reads stdin and writes only the transformed text to stdout. Neither mode can be
combined with a file or output path.

## Python API

`transform_text(source)` regularizes complete document bodies or fragments.
