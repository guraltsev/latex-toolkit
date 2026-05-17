# `dmath_eqnum2eqn`

`dmath_eqnum2eqn` is the reverse-direction alias for `eqn2dmath_eqnum`. It
rewrites `\[\eqnum ... \]` display-math blocks as `equation` environments and
does not expose its own `--reverse` option. Its historical help and log label
is `dmath-eqnum2eqn`.

## Use Cases

- Convert the local numbered display-math convention back to standard
  `equation` environments.
- Run the same reverse conversion that `eqn2dmath_eqnum --reverse` would run.

## Usage

```powershell
python -m latex_toolkit.commands.dmath_eqnum2eqn .\paper.tex
python -m latex_toolkit.commands.dmath_eqnum2eqn .\paper.tex -o .\paper.converted.tex
python -m latex_toolkit.commands.dmath_eqnum2eqn --clipboard
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
\[\eqnum x+y\]
```

Output:

```tex
\begin{equation} x+y\end{equation}
```

Preserved plain display:

```tex
\[x+y\]
```

## Behavior Notes

- This command calls `eqn2dmath_eqnum` with reverse direction forced.
- By default, file mode overwrites the input after creating a timestamped
  backup under `.backup`.
- Only display-math blocks whose body begins with standalone `\eqnum` are
  converted.
- Plain display math is intentionally left untouched.
- Nested matching constructs are converted recursively.
- When a balanced `document` environment is present, only the document body is
  rewritten.

## Python API

Use `latex_toolkit.commands.dmath_eqnum2eqn.main.transform_text(text)` to run
the forced reverse conversion.

## Related Commands

- `eqn2dmath_eqnum` owns the shared parser and transform.
- `dmath2eqn_star` handles plain unnumbered display-math blocks.
