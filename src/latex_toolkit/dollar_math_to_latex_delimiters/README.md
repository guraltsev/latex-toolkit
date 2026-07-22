# dollar_math_to_latex_delimiters

Convert `$...$` and `$$...$$` math delimiters to `\(...\)` and `\[...\]`.
Only top-level document bodies change in complete LaTeX documents.

## Usage

```powershell
python -m latex_toolkit.dollar_math_to_latex_delimiters .\paper.tex
python -m latex_toolkit.dollar_math_to_latex_delimiters .\paper.tex -o .\paper.out.tex
python -m latex_toolkit.dollar_math_to_latex_delimiters --clipboard
Get-Content .\paper.tex -Raw | python -m latex_toolkit.dollar_math_to_latex_delimiters --stdin
```

Without an output path, file mode writes `paper_latex_delimiters.tex` beside
the source. Clipboard mode replaces nonempty clipboard text. Standard-stream
mode reads stdin and writes only the transformed text to stdout. Neither mode
can be combined with a file or output path.

## Python API

`transform_text(source)` converts document bodies or LaTeX fragments. See
`latex_delimiters_to_dollar_math` for the reverse transformation.
