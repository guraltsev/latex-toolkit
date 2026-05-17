# `dollar2bracket`

`dollar2bracket` rewrites matched `$...$` and `$$...$$` math delimiters as
`\(...\)` and `\[...\]`. With `--reverse`, it rewrites matched bracket
delimiters back to dollar delimiters.

## Use Cases

- Normalize dollar-delimited LaTeX into bracket delimiters before editing.
- Reverse bracket delimiters back to dollar delimiters for systems that prefer
  the older form.

## Usage

```powershell
python -m latex_toolkit.commands.dollar2bracket .\paper.tex
python -m latex_toolkit.commands.dollar2bracket .\paper.tex --reverse
python -m latex_toolkit.commands.dollar2bracket .\paper.tex -o .\paper.converted.tex
python -m latex_toolkit.commands.dollar2bracket --clipboard
```

The command supports file mode and clipboard mode.

## Options

| Option | Meaning |
| --- | --- |
| `input` | Optional `.tex` path in file mode. Required unless `--clipboard` is used. |
| `--clipboard` | Read LaTeX from the system clipboard and replace the clipboard with converted text. It rejects simultaneous input or output paths. |
| `--reverse` | Convert `\(...\)` and `\[...\]` back to `$...$` and `$$...$$`. |
| `-o`, `--output`, `--output-file` | Write converted text to a separate path without changing the source file or creating a backup. |
| `-B`, `--no-backup` | Skip backup creation when overwriting the input file. |
| `--backup-dir` | Backup directory used only when overwriting the input. Defaults to `.backup`. |

## Examples

Input:

```tex
Inline $x+1$ and display $$x^2$$ remain paired. Escaped \$ stays.
```

Output:

```tex
Inline \(x+1\) and display \[x^2\] remain paired. Escaped \$ stays.
```

## Behavior Notes

- By default, file mode overwrites the input after creating a timestamped
  backup under `.backup`.
- Only matched delimiter pairs of the same kind are rewritten.
- Escaped dollar signs, comments, and unmatched delimiters are preserved.
- Reverse mode avoids linebreak options such as `\\[0.5em]`.
- When a balanced `document` environment is present, only the document body is
  rewritten.

## Python API

Use `latex_toolkit.commands.dollar2bracket.main.transform_text(text,
reverse=False)` to convert raw text. Pass `reverse=True` for bracket-to-dollar
conversion.

## Related Commands

- `bracket2dollar` is the reverse-direction alias for this command.
- `texmacs_latex_to_llm_latex` uses this command as its first pipeline step.
