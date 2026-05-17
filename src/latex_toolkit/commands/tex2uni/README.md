# `tex2uni`

`tex2uni` converts a mapped set of LaTeX math macros inside mutable math-mode
content to Unicode symbols. With `--reverse`, it converts the same mapped
Unicode symbols back to LaTeX macros.

## Use Cases

- Make math-heavy snippets more compact for editing or LLM workflows.
- Reverse a Unicode-heavy math snippet back to ASCII LaTeX macros.

## Usage

```powershell
python -m latex_toolkit.commands.tex2uni .\paper.tex
python -m latex_toolkit.commands.tex2uni .\paper.tex --reverse
python -m latex_toolkit.commands.tex2uni .\paper.tex -o .\paper.unicode.tex
python -m latex_toolkit.commands.tex2uni --clipboard
```

The command supports file mode and clipboard mode.

## Options

| Option | Meaning |
| --- | --- |
| `input` | Optional `.tex` path in file mode. Required unless `--clipboard` is used. |
| `--clipboard` | Read LaTeX from the system clipboard and replace the clipboard with converted text. It rejects simultaneous input or output paths. |
| `--reverse` | Convert mapped Unicode symbols back to LaTeX macros. |
| `-o`, `--output`, `--output-file` | Write converted text to a separate path without changing the source file or creating a backup. |
| `-B`, `--no-backup` | Skip backup creation when overwriting the input file. |
| `--backup-dir` | Backup directory used only when overwriting the input. Defaults to `.backup`. |

## Examples

Input:

```tex
Text \alpha outside math, but $\alpha \leq \beta$ inside math.
```

Output:

```tex
Text \alpha outside math, but $α ≤ β$ inside math.
```

Reverse output from `--reverse`:

```tex
Text \alpha outside math, but $\alpha  \leq  \beta $ inside math.
```

## Behavior Notes

- By default, file mode overwrites the input after creating a timestamped
  backup under `.backup`.
- Conversion happens only while the scanner is inside math delimiters or known
  math environments.
- `%` comments are preserved verbatim.
- When a balanced `document` environment is present, only the document body is
  rewritten.
- The mapping is intentionally finite; unmapped macros and Unicode characters
  are preserved.
- Reverse conversion emits a trailing space after each generated LaTeX macro
  to preserve token boundaries.

## Python API

Use `latex_toolkit.commands.tex2uni.main.transform_text(text, reverse=False)`
to convert raw text. Pass `reverse=True` for Unicode-to-LaTeX conversion.

## Related Commands

- `uni2tex` is the reverse-direction alias for this command.
- `texmacs_latex_to_llm_latex` runs `uni2tex` as the final clipboard pipeline
  step.
