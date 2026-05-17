# `bracket2dollar`

`bracket2dollar` is the reverse-direction alias for `dollar2bracket`. It
rewrites matched `\(...\)` and `\[...\]` math delimiters back to `$...$` and
`$$...$$` and does not expose its own `--reverse` option.

## Use Cases

- Convert bracket-delimited LaTeX back to dollar delimiters.
- Run the same reverse conversion that `dollar2bracket --reverse` would run.

## Usage

```powershell
python -m latex_toolkit.commands.bracket2dollar .\paper.tex
python -m latex_toolkit.commands.bracket2dollar .\paper.tex -o .\paper.converted.tex
python -m latex_toolkit.commands.bracket2dollar --clipboard
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
Inline \(x+1\) and display \[x^2\]. Linebreak \\[0.5em] stays.
```

Output:

```tex
Inline $x+1$ and display $$x^2$$. Linebreak \\[0.5em] stays.
```

## Behavior Notes

- This command calls `dollar2bracket` with reverse direction forced.
- By default, file mode overwrites the input after creating a timestamped
  backup under `.backup`.
- Only matched delimiter pairs are rewritten.
- Comments, unmatched delimiters, and linebreak options such as `\\[0.5em]`
  are preserved.
- When a balanced `document` environment is present, only the document body is
  rewritten.

## Python API

Use `latex_toolkit.commands.bracket2dollar.main.transform_text(text)` to run
the forced reverse conversion.

## Related Commands

- `dollar2bracket` owns the shared parser and transform.
