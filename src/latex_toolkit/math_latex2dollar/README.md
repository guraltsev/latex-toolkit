# math_latex2dollar

Convert parsed command-delimited math without modifying its contents: inline
`\(...\)` becomes `$...$`, and display `\[...\]` becomes `$$...$$`. The
conversion changes delimiters only, so unrelated text and non-target math
syntax remain as written.

In complete LaTeX documents, only math in top-level `document` bodies changes;
the preamble remains untouched. Input without a `document` environment is
treated as a fragment. This is the exact reverse of `math_dollar2latex` for
supported math delimiters.

## Use Cases

- Convert command-style math delimiters to dollar syntax for a downstream tool.
- Reverse a `math_dollar2latex` conversion.

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

## Options

| Option | Meaning |
| --- | --- |
| `input` | UTF-8 LaTeX file to convert. |
| `-o`, `--output`, `--output-file` | Write a separate result and preserve the input. |
| `--clipboard` | Transform nonempty clipboard text. |
| `--stdin` | Read stdin and write only converted source to stdout. |
| `-B`, `--no-backup` | Skip the backup when overwriting the input. |

## Examples

`\(x\)` becomes `$x$` and `\[y\]` becomes `$$y$$`; their contents are unchanged.

## Behavior Notes

Only parsed command-style math delimiters in document bodies or fragments are
changed. Unmatched or unrelated source is preserved.

## Related Commands

`math_dollar2latex` performs the reverse conversion.
