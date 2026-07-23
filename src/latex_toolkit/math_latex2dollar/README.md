# math_latex2dollar

Convert parsed command-delimited math without modifying its contents: inline
`\(...\)` becomes `$...$`, and display `\[...\]` becomes `$$...$$`. The
conversion changes delimiters only, so unrelated text and non-target math
syntax remain as written.

In complete LaTeX documents, only math in top-level `document` bodies changes;
the preamble remains untouched. Input without a `document` environment is
treated as a fragment. This is the exact reverse of `math_dollar2latex` for
supported math delimiters.

## Usage

```powershell
python -m latex_toolkit.math_latex2dollar .\paper.tex
python -m latex_toolkit.math_latex2dollar .\paper.tex -o .\paper.out.tex
python -m latex_toolkit.math_latex2dollar --clipboard
Get-Content .\paper.tex -Raw | python -m latex_toolkit.math_latex2dollar --stdin
```

Without an output path, file mode writes `paper_dollar_math.tex` beside the
source. Clipboard mode replaces nonempty clipboard text. Standard-stream mode
reads stdin and writes only the transformed text to stdout. Neither mode can be
combined with a file or output path.

## Python API

`transform_text(source)` converts document bodies or LaTeX fragments.
