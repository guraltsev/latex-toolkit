# full_normalize

Apply the toolkit's complete layout-normalization pipeline: syntax
regularization, prose sentence-per-line formatting, then syntax regularization
again. The first and last stages remove ordinary indentation, unwrap eligible
inline math, and normalize structural line breaks; the middle stage joins
wrapped prose and starts each sentence on its own line. The final pass ensures
the sentence formatter's output follows the same syntax-layout rules.

The pipeline preserves protected math, table-like, verbatim-like, and
structural source regions according to its component commands. In complete
documents it changes only top-level `document` bodies; fragments are processed
in full. It requires `snapper-fmt` through the sentence-formatting stage.

## Use Cases

- Apply the toolkit's syntax and prose layout conventions in one pipeline.
- Normalize fragments or complete document bodies before review or publication.

## Usage

```powershell
python -m latex_toolkit.full_normalize .\paper.tex
python -m latex_toolkit.full_normalize .\paper.tex -o .\paper.out.tex
python -m latex_toolkit.full_normalize --clipboard
Get-Content .\paper.tex -Raw | python -m latex_toolkit.full_normalize --stdin
```

Without an output path, file mode writes `paper_full_normalized.tex` beside the
source. Clipboard mode replaces nonempty clipboard text. Standard-stream mode
reads stdin and writes only the transformed text to stdout. Neither mode can be
combined with a file or output path.

## Python API

`transform_text(source)` runs the complete pipeline in memory.

## Options

| Option | Meaning |
| --- | --- |
| `input` | UTF-8 LaTeX file to transform in place. |
| `-o`, `--output`, `--output-file` | Write a separate result and preserve the input. |
| `--clipboard` | Transform nonempty clipboard text. |
| `--stdin` | Read all source from stdin and write only transformed source to stdout. |
| `-B`, `--no-backup` | Skip the timestamped backup when overwriting the input. |

## Examples

Wrapped prose is joined within a sentence, while sentence boundaries become
physical line breaks and syntax regularization is applied before and after.

## Behavior Notes

The pipeline requires `snapper-fmt`; failures leave the destination unopened.
Protected regions follow the contracts of `syntax_regularizer` and
`sentence_per_line`.

## Related Commands

`syntax_regularizer` and `sentence_per_line` are the component commands used by
this pipeline.
