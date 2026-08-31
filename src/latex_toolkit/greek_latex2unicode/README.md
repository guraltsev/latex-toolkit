# greek_latex2unicode

Convert conventional LaTeX Greek macros and selected common math macros to
Unicode symbols only in parsed math mode. This is the reverse of
`greek_unicode2latex` and preserves prose, comments, and complete-document
preambles.

## Use Cases

- Convert recognized Greek control words for Unicode-aware editing or analysis.
- Convert canonical and alias spellings such as `\emptyset`/`\varnothing`,
  `\setminus`/`\smallsetminus`, `\leq`/`\le`, `\wedge`/`\land`, and
  `\to`/`\rightarrow`.
- Reverse a `greek_unicode2latex` conversion.

## Usage

```powershell
python -m latex_toolkit.greek_latex2unicode .\paper.tex
python -m latex_toolkit.greek_latex2unicode --clipboard
Get-Content .\paper.tex -Raw | python -m latex_toolkit.greek_latex2unicode --stdin
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

`$\alpha + \Omega$` becomes `$α + Ω$`, while the same macros in prose remain unchanged.

## Behavior Notes

Only parsed math delimiters and supported math environments are changed.
Complete-document preambles, prose, comments, and unsupported macros are preserved.

## Related Commands

`greek_unicode2latex` performs the opposite direction.
