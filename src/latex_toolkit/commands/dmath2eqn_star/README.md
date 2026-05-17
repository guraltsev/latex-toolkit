# `dmath2eqn_star`

`dmath2eqn_star` is the reverse-direction alias for `eqn_star2dmath`. It
rewrites plain `\[ ... \]` display math as `equation*` environments and does
not expose its own `--reverse` option. Its historical help and log label is
`dmath2eqn-star`.

## Use Cases

- Expand plain display math into explicit unnumbered equation environments.
- Run the same reverse conversion that `eqn_star2dmath --reverse` would run.

## Usage

```powershell
python -m latex_toolkit.commands.dmath2eqn_star .\paper.tex
python -m latex_toolkit.commands.dmath2eqn_star .\paper.tex -o .\paper.converted.tex
python -m latex_toolkit.commands.dmath2eqn_star --clipboard
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
\[x+y\]
```

Output:

```tex
\begin{equation*}x+y\end{equation*}
```

Preserved numbered display:

```tex
\[\eqnum x+y\]
```

## Behavior Notes

- This command calls `eqn_star2dmath` with reverse direction forced.
- By default, file mode overwrites the input after creating a timestamped
  backup under `.backup`.
- Only plain display-math blocks are rewritten.
- Display-math blocks whose body begins with standalone `\eqnum` are preserved
  for the numbered-equation workflow.
- Nested matching constructs are converted recursively.
- When a balanced `document` environment is present, only the document body is
  rewritten.

## Python API

Use `latex_toolkit.commands.dmath2eqn_star.main.transform_text(text)` to run
the forced reverse conversion.

## Related Commands

- `eqn_star2dmath` owns the shared parser and transform.
- `dmath_eqnum2eqn` handles numbered display-math blocks.
