# latex_delimiters_to_dollar_math

Convert `\(...\)` and `\[...\]` math delimiters to `$...$` and `$$...$$`.
This reverse command delegates to the dollar-math command family.

## Usage

```powershell
python -m latex_toolkit.latex_delimiters_to_dollar_math .\paper.tex
python -m latex_toolkit.latex_delimiters_to_dollar_math .\paper.tex -o .\paper.out.tex
python -m latex_toolkit.latex_delimiters_to_dollar_math --clipboard
Get-Content .\paper.tex -Raw | python -m latex_toolkit.latex_delimiters_to_dollar_math --stdin
```

Without an output path, file mode writes `paper_dollar_math.tex` beside the
source. Clipboard mode replaces nonempty clipboard text. Standard-stream mode
reads stdin and writes only the transformed text to stdout. Neither mode can be
combined with a file or output path.

## Python API

`transform_text(source)` converts document bodies or LaTeX fragments.
