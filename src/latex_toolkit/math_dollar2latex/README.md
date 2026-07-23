# math_dollar2latex

Convert parsed dollar-delimited math without modifying its contents: inline
`$...$` becomes `\(...\)`, and display `$$...$$` becomes `\[...\]`. Because
the conversion is parser-based, escaped dollar signs, comments, literal text,
and already command-delimited math are not mistaken for targets.

In complete LaTeX documents, only math in top-level `document` bodies changes;
the preamble remains untouched. Input without a `document` environment is
treated as a fragment. See `math_latex2dollar` for the exact reverse conversion.

## Usage

```powershell
python -m latex_toolkit.math_dollar2latex .\paper.tex
python -m latex_toolkit.math_dollar2latex .\paper.tex -o .\paper.out.tex
python -m latex_toolkit.math_dollar2latex --clipboard
Get-Content .\paper.tex -Raw | python -m latex_toolkit.math_dollar2latex --stdin
```

Without an output path, file mode writes `paper_latex_delimiters.tex` beside
the source. Clipboard mode replaces nonempty clipboard text. Standard-stream
mode reads stdin and writes only the transformed text to stdout. Neither mode
can be combined with a file or output path.

## Python API

`transform_text(source)` converts document bodies or LaTeX fragments.
