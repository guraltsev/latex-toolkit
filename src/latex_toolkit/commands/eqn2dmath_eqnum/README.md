# `eqn2dmath_eqnum`

`eqn2dmath_eqnum` converts between balanced numbered `equation` environments
and the project convention `\[\eqnum ... \]`. Its historical help and log
label is `eqn2dmath-eqnum`.

## Use Cases

- Convert numbered equation environments into the local display-math plus
  `\eqnum` marker form.
- Reverse only those marked display-math blocks back to `equation`
  environments.

## Usage

```powershell
python -m latex_toolkit.commands.eqn2dmath_eqnum .\paper.tex
python -m latex_toolkit.commands.eqn2dmath_eqnum .\paper.tex --reverse
python -m latex_toolkit.commands.eqn2dmath_eqnum .\paper.tex -o .\paper.converted.tex
python -m latex_toolkit.commands.eqn2dmath_eqnum --clipboard
```

The command supports file mode and clipboard mode.

## Options

| Option | Meaning |
| --- | --- |
| `input` | Optional `.tex` path in file mode. Required unless `--clipboard` is used. |
| `--clipboard` | Read LaTeX from the system clipboard and replace the clipboard with converted text. It rejects simultaneous input or output paths. |
| `--reverse` | Convert display-math blocks whose body begins with standalone `\eqnum` back to `equation` environments. |
| `-o`, `--output`, `--output-file` | Write converted text to a separate path without changing the source file or creating a backup. |
| `-B`, `--no-backup` | Skip backup creation when overwriting the input file. |
| `--backup-dir` | Backup directory used only when overwriting the input. Defaults to `.backup`. |

## Examples

Input:

```tex
\begin{equation}x+y\end{equation}
```

Output:

```tex
\[\eqnum x+y\]
```

Reverse input:

```tex
\[\eqnum x+y\]
```

Reverse output:

```tex
\begin{equation} x+y\end{equation}
```

## Behavior Notes

- By default, file mode overwrites the input after creating a timestamped
  backup under `.backup`.
- Forward conversion rewrites only balanced `equation` environments.
- Forward conversion inserts a standalone `\eqnum` marker at the start of each
  converted display-math body.
- Reverse conversion rewrites only display-math blocks whose body begins with
  standalone `\eqnum`; plain `\[ ... \]` blocks are preserved.
- Nested matching constructs are converted recursively.
- When a balanced `document` environment is present, only the document body is
  rewritten.

## Python API

Use `latex_toolkit.commands.eqn2dmath_eqnum.main.transform_text(text,
reverse=False)` to convert raw text. Pass `reverse=True` for `\eqnum`
display-math to `equation` conversion.

## Related Commands

- `dmath_eqnum2eqn` is the reverse-direction alias for this command.
- `eqn_star2dmath` handles unnumbered `equation*` environments.
