# `manual_latex_reformat`

`manual_latex_reformat` reformats supported LaTeX math environments with the
spacing and line-breaking rules from `Discovery/manual_latex_reformat.py`.

## Usage

```powershell
python -m latex_toolkit.commands.manual_latex_reformat
python -m latex_toolkit.commands.manual_latex_reformat --clipboard
python -m latex_toolkit.commands.manual_latex_reformat .\paper.tex
python -m latex_toolkit.commands.manual_latex_reformat .\paper.tex -o .\paper.reformatted.tex
.\manual_latex_reformat.cmd
```

The command supports file mode and clipboard mode. With no input path, it uses
clipboard text by default so the Windows launcher works on copied LaTeX without
an extra flag.

## Options

| Option | Meaning |
| --- | --- |
| `input` | Optional `.tex` path in file mode. When omitted, the command processes the clipboard unless `--clipboard` is used. |
| `--clipboard` | Read LaTeX from the system clipboard and replace the clipboard with reformatted output. It rejects simultaneous input or output paths. |
| `--max-width` | Maximum formatted math line length before splitting. Defaults to `95`. |
| `-o`, `--output`, `--output-file` | Write reformatted output to a separate path without changing the source file or creating a backup. |
| `-B`, `--no-backup` | Skip backup creation when overwriting the input file. |
| `--backup-dir` | Backup directory used only when overwriting the input. Defaults to `.backup`. |
