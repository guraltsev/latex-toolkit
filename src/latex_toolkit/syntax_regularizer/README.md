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

## Use Cases

- Apply consistent physical-line layout to LaTeX source before formatting review.
- Regularize prose and delimiters while protecting math and structural regions.

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

## Options

| Option | Meaning |
| --- | --- |
| `input` | UTF-8 LaTeX file to regularize. |
| `-o`, `--output`, `--output-file` | Write a separate result and preserve the input. |
| `--clipboard` | Transform nonempty clipboard text. |
| `--stdin` | Read stdin and write only regularized source to stdout. |
| `-B`, `--no-backup` | Skip the backup when overwriting the input. |

## Examples

Indented prose is left-aligned, while eligible inline math is unwrapped and
display delimiters are isolated on their own lines.

## Behavior Notes

Math containing comments, display math contents, tables, and verbatim-like
environments retain their protected layout. Unsafe incomplete input is unchanged.

## Related Commands

`full_normalize` applies this command before and after `sentence_per_line`.
