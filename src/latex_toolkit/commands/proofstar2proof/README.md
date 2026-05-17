# `proofstar2proof`

`proofstar2proof` rewrites titled TeXmacs `\begin{proof*}{Title} ...
\end{proof*}` environments as standard `\begin{proof}[Title] ...
\end{proof}` environments. With `--reverse`, it rewrites titled `proof`
environments back to `proof*`.

## Use Cases

- Convert TeXmacs proof environments into ordinary LaTeX proof environments.
- Reverse titled proof environments before importing edited text back into
  TeXmacs.

## Usage

```powershell
python -m latex_toolkit.commands.proofstar2proof .\paper.tex
python -m latex_toolkit.commands.proofstar2proof .\paper.tex --reverse
python -m latex_toolkit.commands.proofstar2proof .\paper.tex -o .\paper.converted.tex
python -m latex_toolkit.commands.proofstar2proof --clipboard
```

The command supports file mode and clipboard mode.

## Options

| Option | Meaning |
| --- | --- |
| `input` | Optional `.tex` path in file mode. Required unless `--clipboard` is used. |
| `--clipboard` | Read LaTeX from the system clipboard and replace the clipboard with converted text. It rejects simultaneous input or output paths. |
| `--reverse` | Convert titled `proof` environments back to TeXmacs `proof*` environments. |
| `-o`, `--output`, `--output-file` | Write converted text to a separate path without changing the source file or creating a backup. |
| `-B`, `--no-backup` | Skip backup creation when overwriting the input file. |
| `--backup-dir` | Backup directory used only when overwriting the input. Defaults to `.backup`. |

## Examples

Input:

```tex
\begin{proof*}{Claim}Done.\end{proof*}
```

Output:

```tex
\begin{proof}[Claim]Done.\end{proof}
```

Reverse input:

```tex
\begin{proof}[Claim]Done.\end{proof}
```

Reverse output:

```tex
\begin{proof*}{Claim}Done.\end{proof*}
```

## Behavior Notes

- By default, file mode overwrites the input after creating a timestamped
  backup under `.backup`.
- Forward conversion rewrites only complete `proof*` environments with a
  balanced mandatory title group.
- Reverse conversion rewrites only complete `proof` environments with a
  balanced optional title group.
- Untitled proofs, malformed title groups, and unmatched environments are
  preserved.
- Matching proof environments can be nested and are converted recursively.
- When a balanced `document` environment is present, only the document body is
  rewritten.

## Python API

Use `latex_toolkit.commands.proofstar2proof.main.transform_text(text,
reverse=False)` to convert raw text. Pass `reverse=True` for `proof` to
`proof*` conversion.

## Related Commands

- `proof2proofstar` is the reverse-direction alias for this command.
- `texmacs_latex_to_llm_latex` runs this command after `tmscript2substack`.
