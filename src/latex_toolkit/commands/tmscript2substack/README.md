# `tmscript2substack`

`tmscript2substack` rewrites TeXmacs centered script arrays of the form
`\tmscript{\begin{array}{c} ... \end{array}}` into `\substack{...}` calls.

## Use Cases

- Convert TeXmacs-generated stacked scripts into conventional LaTeX.
- Prepare copied TeXmacs LaTeX for easier manual or LLM editing.

## Usage

```powershell
python -m latex_toolkit.commands.tmscript2substack .\paper.tex
python -m latex_toolkit.commands.tmscript2substack .\paper.tex -o .\paper.converted.tex
python -m latex_toolkit.commands.tmscript2substack --clipboard
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
\tmscript{\begin{array}{c}i\\j\end{array}}
```

Output:

```tex
\substack{i\\j}
```

## Behavior Notes

- By default, file mode overwrites the input after creating a timestamped
  backup under `.backup`.
- Only complete `\tmscript` calls whose argument is a centered `array`
  environment are converted.
- Non-centered arrays, malformed array snippets, and other `\tmscript` uses are
  preserved.
- Matching constructs can be nested and are converted recursively.
- When a balanced `document` environment is present, only the document body is
  rewritten.

## Python API

Use `latex_toolkit.commands.tmscript2substack.main.transform_text(text)` to
convert raw LaTeX text.

## Related Commands

- `texmacs_latex_to_llm_latex` runs this command after `ltae2aligned`.
