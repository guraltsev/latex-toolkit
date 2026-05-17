# `baea2aligned`

`baea2aligned` is the reverse-direction alias for `aligned2baea`. It expands
literal `\ba` / `\ea` control words into `\begin{aligned}[t]` /
`\end{aligned}` and does not expose its own `--reverse` option.

## Use Cases

- Expand local shorthand before sharing source with tools that expect explicit
  environments.
- Run the same reverse conversion that `aligned2baea --reverse` would run.

## Usage

```powershell
python -m latex_toolkit.commands.baea2aligned .\paper.tex
python -m latex_toolkit.commands.baea2aligned .\paper.tex -o .\paper.expanded.tex
python -m latex_toolkit.commands.baea2aligned --clipboard
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
\ba x&=y\ea
```

Output:

```tex
\begin{aligned}[t] x&=y\end{aligned}
```

## Behavior Notes

- This command calls `aligned2baea` with reverse direction forced.
- By default, file mode overwrites the input after creating a timestamped
  backup under `.backup`.
- The conversion expands literal `\ba` and `\ea` control words only when a
  control-word boundary is present.
- Comments are preserved verbatim.
- When a balanced `document` environment is present, only the document body is
  rewritten.

## Python API

Use `latex_toolkit.commands.baea2aligned.main.transform_text(text)` to run the
forced reverse conversion.

## Related Commands

- `aligned2baea` owns the shared parser and transform.
