# math_dollar2latex

Convert parsed dollar-delimited math without modifying its contents: inline
`$...$` becomes `\(...\)`, and display `$$...$$` becomes `\[...\]`. Because
the conversion is parser-based, escaped dollar signs, comments, literal text,
and already command-delimited math are not mistaken for targets.

In complete LaTeX documents, only math in top-level `document` bodies changes;
the preamble remains untouched. Input without a `document` environment is
treated as a fragment. See `math_latex2dollar` for the exact reverse conversion.

## Use Cases

- Standardize dollar-delimited math to command-style LaTeX delimiters.
- Convert formulas before tools that distinguish inline and display commands.

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

## Options

| Option | Meaning |
| --- | --- |
| `input` | UTF-8 LaTeX file to convert. |
| `-o`, `--output`, `--output-file` | Write a separate result and preserve the input. |
| `--clipboard` | Transform nonempty clipboard text. |
| `--stdin` | Read stdin and write only converted source to stdout. |
| `-B`, `--no-backup` | Skip the backup when overwriting the input. |

## Examples

`$x$` becomes `\(x\)` and `$$y$$` becomes `\[y\]`; their contents are unchanged.

## Behavior Notes

Only parsed math delimiters in document bodies or fragments are changed.
Escaped dollars, comments, and already command-delimited math are preserved.

## Related Commands

`math_latex2dollar` performs the reverse conversion.
