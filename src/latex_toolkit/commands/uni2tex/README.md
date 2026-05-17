# `uni2tex`

`uni2tex` is the reverse-direction alias for `tex2uni`. It converts mapped
Unicode math symbols inside mutable math-mode content back to LaTeX macros and
does not expose its own `--reverse` option.

## Use Cases

- Convert Unicode math symbols back to ASCII LaTeX before TeXmacs import or
  conservative source sharing.
- Run the same reverse conversion that `tex2uni --reverse` would run.

## Usage

```powershell
python -m latex_toolkit.commands.uni2tex .\paper.tex
python -m latex_toolkit.commands.uni2tex .\paper.tex -o .\paper.ascii.tex
python -m latex_toolkit.commands.uni2tex --clipboard
```

The command supports file mode and clipboard mode.

## Options

| Option | Meaning |
| --- | --- |
| `input` | Optional `.tex` path in file mode. Required unless `--clipboard` is used. |
| `--clipboard` | Read LaTeX from the system clipboard and replace the clipboard with converted text. It rejects simultaneous input or output paths. |
| `-o`, `--output`, `--output-file` | Write converted text to a separate path without changing the source file or creating a backup. |
| `-B`, `--no-backup` | Skip backup creation when overwriting the input file. |
| `--backup-dir` | Backup directory used only when overwriting the input. Defaults to `.backup`. |

## Examples

Input:

```tex
Outside α stays, but $α ≤ β$ changes.
```

Output:

```tex
Outside α stays, but $\alpha  \leq  \beta $ changes.
```

## Behavior Notes

- This command calls `tex2uni` with reverse direction forced.
- By default, file mode overwrites the input after creating a timestamped
  backup under `.backup`.
- Conversion happens only while the scanner is inside math delimiters or known
  math environments.
- `%` comments are preserved verbatim.
- When a balanced `document` environment is present, only the document body is
  rewritten.
- Reverse conversion emits a trailing space after each generated LaTeX macro
  to preserve token boundaries.

## Python API

Use `latex_toolkit.commands.uni2tex.main.transform_text(text)` to run the
forced reverse conversion.

## Related Commands

- `tex2uni` owns the shared parser and transform.
- `texmacs_latex_to_llm_latex` uses this command's transform at the end of its
  clipboard pipeline.
