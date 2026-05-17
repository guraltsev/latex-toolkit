# `ltae2aligned`

`ltae2aligned` rewrites balanced `\begin{ltae} ... \end{ltae}`
environments as explicit `\begin{aligned}[t] ... \end{aligned}` blocks and
adds leading alignment markers to top-level rows.

## Use Cases

- Convert TeXmacs-generated `ltae` environments into ordinary LaTeX
  `aligned[t]` blocks.
- Prepare TeXmacs LaTeX for the `aligned2baea` shorthand workflow.

## Usage

```powershell
python -m latex_toolkit.commands.ltae2aligned .\paper.tex
python -m latex_toolkit.commands.ltae2aligned .\paper.tex -o .\paper.converted.tex
python -m latex_toolkit.commands.ltae2aligned --clipboard
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
\begin{ltae}x\\y\end{ltae}
```

Output:

```tex
\begin{aligned}[t]&x\\&y\end{aligned}
```

## Behavior Notes

- By default, file mode overwrites the input after creating a timestamped
  backup under `.backup`.
- Only balanced `ltae` environments are rewritten.
- A leading `&` is added to the first top-level row and to rows after
  top-level `\\` separators when the row does not already begin with `&`.
- Nested environments such as `cases` keep their own row structure.
- When a balanced `document` environment is present, only the document body is
  rewritten.

## Python API

Use `latex_toolkit.commands.ltae2aligned.main.transform_text(text)` to convert
raw LaTeX text.

## Related Commands

- `texmacs_latex_to_llm_latex` runs this command after `dollar2bracket`.
- `aligned2baea` can compress the resulting `aligned[t]` blocks.
