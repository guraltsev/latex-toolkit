# sentence_per_line

Format LaTeX prose so each sentence occupies one physical line, while joining
ordinary source wrapping within a sentence and retaining paragraph breaks.
Comments, inline and display math, verbatim-like content, and structural
environments retain their original source spelling. Prose in captions and
footnotes is formatted recursively; footnote calls can be placed on their own
lines with TeX comments where necessary to preserve adjacent spacing.

In a complete document, only top-level `document` bodies are formatted; input
without a `document` environment is treated as a fragment. The command
requires `snapper-fmt` and returns incomplete LaTeX input unchanged rather
than attempting a partial rewrite.

## Use Cases

- Keep prose source readable in reviews by placing one sentence on each line.
- Normalize wrapped prose while preserving TeX-sensitive regions.

## Usage

```powershell
python -m latex_toolkit.sentence_per_line .\paper.tex
python -m latex_toolkit.sentence_per_line .\paper.tex -o .\paper.out.tex
python -m latex_toolkit.sentence_per_line --clipboard
Get-Content .\paper.tex -Raw | python -m latex_toolkit.sentence_per_line --stdin
```

Without an output path, file mode writes `paper_sentences.tex` beside the
source. Clipboard mode replaces nonempty clipboard text. Standard-stream mode
reads stdin and writes only the transformed text to stdout. Neither mode can be
combined with a file or output path.

## Python API

`transform_text(source)` formats complete document bodies or fragments.

## Options

| Option | Meaning |
| --- | --- |
| `input` | UTF-8 LaTeX file to format. |
| `-o`, `--output`, `--output-file` | Write a separate result and preserve the input. |
| `--clipboard` | Transform nonempty clipboard text. |
| `--stdin` | Read stdin and write only formatted source to stdout. |
| `-B`, `--no-backup` | Skip the backup when overwriting the input. |

## Examples

`First sentence. Second sentence.` becomes two physical source lines without
changing the sentence text.

## Behavior Notes

The command requires `snapper-fmt`. Incomplete input is returned unchanged;
comments, math, paragraph breaks, and protected environments retain their
source spelling.

## Related Commands

`full_normalize` composes this formatter with `syntax_regularizer`.
