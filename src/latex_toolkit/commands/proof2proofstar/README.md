# `proof2proofstar`

`proof2proofstar` is the reverse-direction alias for `proofstar2proof`. It
rewrites titled `\begin{proof}[Title] ... \end{proof}` environments as
TeXmacs `\begin{proof*}{Title} ... \end{proof*}` environments and does not
expose its own `--reverse` option.

## Use Cases

- Convert titled standard proofs back to TeXmacs `proof*` form.
- Run the same reverse conversion that `proofstar2proof --reverse` would run.

## Usage

```powershell
python -m latex_toolkit.commands.proof2proofstar .\paper.tex
python -m latex_toolkit.commands.proof2proofstar .\paper.tex -o .\paper.converted.tex
python -m latex_toolkit.commands.proof2proofstar --clipboard
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
\begin{proof}[Claim]Done.\end{proof}
```

Output:

```tex
\begin{proof*}{Claim}Done.\end{proof*}
```

## Behavior Notes

- This command calls `proofstar2proof` with reverse direction forced.
- By default, file mode overwrites the input after creating a timestamped
  backup under `.backup`.
- Only titled `proof` environments with balanced optional title groups are
  converted.
- Untitled proofs, malformed title groups, and unmatched environments are
  preserved.
- Matching proof environments can be nested and are converted recursively.
- When a balanced `document` environment is present, only the document body is
  rewritten.

## Python API

Use `latex_toolkit.commands.proof2proofstar.main.transform_text(text)` to run
the forced reverse conversion.

## Related Commands

- `proofstar2proof` owns the shared parser and transform.
- `llm_latex_to_texmacs_latex` runs this command as its final pipeline step.
