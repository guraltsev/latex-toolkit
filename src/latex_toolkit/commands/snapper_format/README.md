# `snapper_format`

`snapper_format` formats LaTeX prose with the external `snapper` semantic line
break formatter so emitted prose lines contain at most one sentence.

## Use Cases

- Reflow prose-heavy LaTeX into semantic line breaks.
- Install or refresh the repository-local `snapper-fmt` runtime used by this
  command.

## Usage

```powershell
python -m latex_toolkit.commands.snapper_format .\paper.tex
python -m latex_toolkit.commands.snapper_format .\paper.tex -o .\paper.snapped.tex
python -m latex_toolkit.commands.snapper_format .\paper.tex --max-width 88
python -m latex_toolkit.commands.snapper_format
python -m latex_toolkit.commands.snapper_format --clipboard
python -m latex_toolkit.commands.snapper_format --install
.\snapper_format.cmd
.\snapper_format.cmd .\paper.tex
```

The command supports file mode, clipboard mode, and install-only mode.

## Options

| Option | Meaning |
| --- | --- |
| `input` | Optional `.tex` path in file mode. When omitted, the command formats the clipboard unless `--install` is used. |
| `--clipboard` | Read LaTeX from the system clipboard and replace the clipboard with formatted text. It rejects simultaneous input or output paths. |
| `--install` | Download or refresh the local `snapper-fmt` runtime, then exit. It cannot be combined with input, output, or `--clipboard`. |
| `--max-width` | Nonnegative wrap width passed to snapper after sentence splitting. The default `0` keeps each sentence on one line. |
| `-o`, `--output`, `--output-file` | Write formatted text to a separate path without changing the source file or creating a backup. |
| `-B`, `--no-backup` | Skip backup creation when overwriting the input file. |
| `--backup-dir` | Backup directory used only when overwriting the input. Defaults to `.backup`. |

## Examples

Input:

```tex
First sentence. Second sentence.
```

Formatted output:

```tex
First sentence.
Second sentence.
```

## Behavior Notes

- The first formatting run installs `snapper-fmt` into
  `src/latex_toolkit/lib/snapper-fmt` if no local snapper executable is found.
- The command runs the executable from that repository-local install directory,
  not from `PATH`.
- With no input path, the command formats clipboard text by default. The root
  `snapper_format.cmd` launcher therefore works on copied text without
  requiring `--clipboard`.
- By default, file mode overwrites the input after creating a timestamped
  backup under `.backup`.
- Snippets without `\begin{document}` are temporarily wrapped as a document for
  snapper and unwrapped after formatting.
- `--max-width` must be zero or positive.
- Snapper installation and formatting failures are reported as command
  failures and leave source files or clipboard contents unchanged.
- The root `snapper_format.cmd` file is a Windows launcher for the Python
  command.

## Python API

Use `latex_toolkit.commands.snapper_format.main.transform_text(text,
max_width=0)` to format raw text. `ensure_snapper()` returns the local snapper
executable, installing it when needed, and `install_snapper()` refreshes the
local runtime.

## Related Commands

- This command is the only command package that depends on the external
  `snapper-fmt` runtime.
