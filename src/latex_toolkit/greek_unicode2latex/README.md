# greek_unicode2latex

Convert Unicode Greek and selected common math symbols to conventional LaTeX
macros only in parsed math mode. Inline/display delimiters and common math
environments are supported; prose, comments, and complete-document preambles
are preserved.

## Use Cases

- Convert Unicode Greek symbols into conventional LaTeX math notation.
- Canonicalize `∅`, `∖`, `≤`, `∧`, and `→` as `\emptyset`, `\setminus`,
  `\leq`, `\wedge`, and `\to`.
- Prepare formulas for workflows that expect LaTeX control words.

## Usage

```powershell
python -m latex_toolkit.greek_unicode2latex .\paper.tex
python -m latex_toolkit.greek_unicode2latex --clipboard
Get-Content .\paper.tex -Raw | python -m latex_toolkit.greek_unicode2latex --stdin
```

`transform_text(source)` returns the converted source.

## Python API

Call `transform_text(source)` for in-memory conversion.

## Options

| Option | Meaning |
| --- | --- |
| `input` | UTF-8 LaTeX file to convert. |
| `--clipboard` | Transform nonempty clipboard text. |
| `--stdin` | Read stdin and write only converted source to stdout. |
| `-o`, `--output`, `--output-file` | Write a separate result. |
| `-B`, `--no-backup` | Skip the backup when overwriting a source file. |

## Examples

`$α + Ω$` becomes `$\alpha + \Omega$`, while Unicode letters in prose remain unchanged.

## Behavior Notes

Only parsed math delimiters and supported math environments are changed.
Complete-document preambles, prose, comments, and unsupported symbols are preserved.

## Related Commands

`greek_latex2unicode` performs the opposite direction.
