# `aligned2baea`

`aligned2baea` converts between exact `\begin{aligned}[t] ...
\end{aligned}` blocks and the local `\ba` / `\ea` shorthand.

## Use Cases

- Compress top-aligned `aligned` environments into the local shorthand used in
  older notes.
- Reverse that shorthand back to explicit LaTeX environments.

## Usage

```powershell
python -m latex_toolkit.commands.aligned2baea .\paper.tex
python -m latex_toolkit.commands.aligned2baea .\paper.tex --reverse
python -m latex_toolkit.commands.aligned2baea .\paper.tex -o .\paper.converted.tex
python -m latex_toolkit.commands.aligned2baea --clipboard
```

The command supports file mode and clipboard mode.

## Options

| Option | Meaning |
| --- | --- |
| `input` | Optional `.tex` path in file mode. Required unless `--clipboard` is used. |
| `--clipboard` | Read LaTeX from the system clipboard and replace the clipboard with converted text. It rejects simultaneous input or output paths. |
| `--reverse` | Expand literal `\ba` / `\ea` control words into `aligned[t]` environments. |
| `-o`, `--output`, `--output-file` | Write converted text to a separate path without changing the source file or creating a backup. |
| `-B`, `--no-backup` | Skip backup creation when overwriting the input file. |
| `--backup-dir` | Backup directory used only when overwriting the input. Defaults to `.backup`. |

## Examples

Input:

```tex
\begin{aligned}[t]x&=y\end{aligned}
```

Output:

```tex
\ba x&=y\ea
```

Reverse input:

```tex
\ba x&=y\ea
```

Reverse output:

```tex
\begin{aligned}[t] x&=y\end{aligned}
```

## Behavior Notes

- By default, file mode overwrites the input after creating a timestamped
  backup under `.backup`.
- Forward conversion only compresses exact `[t]` option forms.
- Nested exact `aligned[t]` environments are converted recursively.
- Reverse conversion is a literal, boundary-aware replacement over mutable
  regions; comments and structural tokens are preserved.
- When a balanced `document` environment is present, only the document body is
  rewritten.

## Python API

Use `latex_toolkit.commands.aligned2baea.main.transform_text(text,
reverse=False)` to convert raw text. Pass `reverse=True` to expand shorthand.

## Related Commands

- `baea2aligned` is the reverse-direction alias for this command.
- `ltae2aligned` produces explicit `aligned[t]` blocks that this command can
  compress.
