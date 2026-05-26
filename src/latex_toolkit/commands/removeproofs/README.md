# `removeproofs`

`removeproofs` removes `proof` and `proof*` environments, including their
contents, from LaTeX source. It parses the input with `pylatexenc` and
installs that dependency into a user-writable cache the first time it is
needed.

## Usage

```powershell
python -m latex_toolkit.commands.removeproofs .\paper.tex
python -m latex_toolkit.commands.removeproofs .\paper.tex -o .\paper.clean.tex
python -m latex_toolkit.commands.removeproofs
python -m latex_toolkit.commands.removeproofs --clipboard
.\removeproofs.cmd
```

The command supports file mode and clipboard mode. With no input path, it
uses clipboard text by default so the Windows launcher works on copied LaTeX
without an extra flag.

## Options

| Option | Meaning |
| --- | --- |
| `input` | Optional `.tex` path in file mode. When omitted, the command processes the clipboard unless `--clipboard` is used. |
| `--clipboard` | Read LaTeX from the system clipboard and replace the clipboard with processed output. It rejects simultaneous input or output paths. |
| `-o`, `--output`, `--output-file` | Write processed output to a separate path without changing the source file or creating a backup. |
| `-B`, `--no-backup` | Skip backup creation when overwriting the input file. |
| `--backup-dir` | Backup directory used only when overwriting the input. Defaults to `.backup`. |

## Behavior Notes

- Proof environments are removed by source span, so surrounding LaTeX is left
  untouched.
- The parser dependency is installed into a user cache under the home
  directory rather than into the repository.
- Parsing failures are reported as command failures.
