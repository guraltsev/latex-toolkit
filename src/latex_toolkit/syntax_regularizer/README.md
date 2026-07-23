# syntax_regularizer

Regularize physical-line layout without changing LaTeX content. It removes
leading indentation from ordinary prose, unwraps uncommented inline math, and
places display-math delimiters, environment openers, and sectioning commands
on their intended lines. Sectioning commands receive one following blank line;
display delimiters are isolated without adding blank lines.

Math containing a real comment is preserved byte-for-byte. The internal layout
of display math, table-like environments, and verbatim-like environments is
also preserved. In complete documents, regularization is limited to top-level
`document` bodies; a fragment is regularized in full. Source that cannot be
parsed safely is returned unchanged.

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
