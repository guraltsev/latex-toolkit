# latex-toolkit

`latex-toolkit` is a small collection of Python commands for editing LaTeX
source files. It is meant to be run directly from this source checkout.

## Running Without Installation

The package is not assumed to be installed. From the repository root, put the
local `src` directory on `PYTHONPATH` for the current PowerShell session:

```powershell
$env:PYTHONPATH = (Resolve-Path .\src).Path
python -m strip_comments .\paper.tex
```

You can also run from `src` directly because Python automatically puts the
current directory on the module search path:

```powershell
cd path\to\latex-toolkit\src
python -m strip_comments ..\paper.tex
```

Use absolute paths or paths relative to your current working directory for TeX
files and output files.

## Command Pattern

Every command can run as a Python package without naming its `main` module:

```powershell
python -m <command_name> <input.tex> [options]
```

Python module names use underscores because they are importable package names:

```powershell
python -m eqn_star2dmath .\paper.tex
python -m eqn2dmath_eqnum .\paper.tex --reverse
```


## File Writes

When a mutating command is given only an input `.tex` path, it overwrites that
file after creating a backup next to it.

Backups are written to `.backup\` subdir and named:

```text
YYYYMMDD-HHMM--filename.ext
```

Write to a separate output file with `--output-file` or `-o`. In that mode, no
backup is created and the input file is left unchanged.

```powershell
python -m latex_toolkit.commands.expand_includes .\main.tex --output-file .\flat.tex
```

Use `-B` or `--no-backup` only when overwriting the input file without creating
a backup is intentional.

## Clipboard Mode

If no input file is provided, the command, if such operations make sense, 
operates in clipboard mode (explicitly requested by --clipboard). The command reads text
from the system clipboard and replaces the clipboard contents with the result.
Do not pass input or output paths with `--clipboard`.

```powershell
python -m tex2uni --clipboard
```
