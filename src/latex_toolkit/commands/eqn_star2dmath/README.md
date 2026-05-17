# `eqn_star2dmath`

`eqn_star2dmath` converts between balanced `equation*` environments and plain
`\[ ... \]` display math. Its historical help and log label is
`eqn-star2dmath`.

## Use Cases

- Collapse unnumbered equation environments into plain display math.
- Reverse plain display math back to explicit `equation*` environments.

## Usage

```powershell
python -m latex_toolkit.commands.eqn_star2dmath .\paper.tex
python -m latex_toolkit.commands.eqn_star2dmath .\paper.tex --reverse
python -m latex_toolkit.commands.eqn_star2dmath .\paper.tex -o .\paper.converted.tex
python -m latex_toolkit.commands.eqn_star2dmath --clipboard
```

The command supports file mode and clipboard mode.

## Options

| Option | Meaning |
| --- | --- |
| `input` | Optional `.tex` path in file mode. Required unless `--clipboard` is used. |
| `--clipboard` | Read LaTeX from the system clipboard and replace the clipboard with converted text. It rejects simultaneous input or output paths. |
| `--reverse` | Convert plain `\[ ... \]` display math back to `equation*` environments. |
| `-o`, `--output`, `--output-file` | Write converted text to a separate path without changing the source file or creating a backup. |
| `-B`, `--no-backup` | Skip backup creation when overwriting the input file. |
| `--backup-dir` | Backup directory used only when overwriting the input. Defaults to `.backup`. |

## Examples

Input:

```tex
\begin{equation*}x+y\end{equation*}
```

Output:

```tex
\[x+y\]
```

Reverse input:

```tex
\[x+y\]
```

Reverse output:

```tex
\begin{equation*}x+y\end{equation*}
```

## Behavior Notes

- By default, file mode overwrites the input after creating a timestamped
  backup under `.backup`.
- Forward conversion rewrites only balanced `equation*` environments.
- Reverse conversion rewrites only plain display-math blocks.
- Reverse conversion intentionally leaves display-math blocks whose body begins
  with standalone `\eqnum` for the numbered-equation workflow.
- Nested matching constructs are converted recursively.
- When a balanced `document` environment is present, only the document body is
  rewritten.

## Python API

Use `latex_toolkit.commands.eqn_star2dmath.main.transform_text(text,
reverse=False)` to convert raw text. Pass `reverse=True` for display-math to
`equation*` conversion.

## Related Commands

- `dmath2eqn_star` is the reverse-direction alias for this command.
- `eqn2dmath_eqnum` handles numbered `equation` environments.
