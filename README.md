# latex-toolkit

`latex-toolkit` is a small collection of Python commands for editing LaTeX
source files. It is meant to be run directly from this source checkout.

## Running Without Installation

The package is not assumed to be installed. From the repository root, put the
local `src` directory on `PYTHONPATH` for the current PowerShell session:

```powershell
$env:PYTHONPATH = (Resolve-Path .\src).Path
python -m latex-toolkit.commands.strip-comments .\paper.tex
```

You can also run from `src` directly because Python automatically puts the
current directory on the module search path:

```powershell
cd path\to\latex-toolkit\src
python -m latex-toolkit.commands.strip-comments ..\paper.tex
```

Use absolute paths or paths relative to your current working directory for TeX
files and output files.

## Command Pattern

Every command can run as a Python package without naming its `main` module:

```powershell
python -m latex-toolkit.commands.<command-name> <input.tex> [options]
```

Command names keep their directory spelling, including hyphens:

```powershell
python -m latex-toolkit.commands.eqn-star2dmath .\paper.tex
python -m latex-toolkit.commands.eqn2dmath-eqnum .\paper.tex --reverse
```

For convenience, the root package also looks inside `commands`, so the shorter
form works too:

```powershell
python -m latex-toolkit.strip-comments .\paper.tex
```

## File Writes

When a mutating command is given only an input `.tex` path, it overwrites that
file after creating a backup next to it.

Backups are written to `.backup` by default and named:

```text
YYYYMMDD-HHMM--filename.ext
```

Write to a separate output file with `--output-file` or `-o`. In that mode, no
backup is created and the input file is left unchanged.

```powershell
python -m latex-toolkit.commands.expand-includes .\main.tex --output-file .\flat.tex
```

Use `-B` or `--no-backup` only when overwriting the input file without creating
a backup is intentional.

## Clipboard Mode

Commands also support `--clipboard`. In clipboard mode, the command reads text
from the system clipboard and replaces the clipboard contents with the result.
Do not pass input or output paths with `--clipboard`.

```powershell
python -m latex-toolkit.commands.tex2uni --clipboard
```

## Commands

### `strip-comments`

Removes LaTeX `%` comments while preserving escaped percent signs such as `\%`.

```powershell
python -m latex-toolkit.commands.strip-comments .\paper.tex
python -m latex-toolkit.commands.strip-comments .\paper.tex -o .\paper.clean.tex
```

### `expand-includes`

Flattens a document by recursively expanding `\input{...}`, `\include{...}`,
`\subfile{...}`, and `\subfileinclude{...}` references.

```powershell
python -m latex-toolkit.commands.expand-includes .\main.tex
python -m latex-toolkit.commands.expand-includes .\main.tex --output-file .\flat.tex
```

### `list-graphics`

Lists `\includegraphics{...}` targets, optionally across recursively included
source files. This command prints to standard output and does not overwrite TeX
files.

```powershell
python -m latex-toolkit.commands.list-graphics .\thesis.tex
python -m latex-toolkit.commands.list-graphics .\thesis.tex --unique
python -m latex-toolkit.commands.list-graphics .\thesis.tex --with-source
python -m latex-toolkit.commands.list-graphics .\thesis.tex --no-recursive
```

### `tex2uni`

Converts mapped LaTeX math macros to Unicode symbols inside mutable math-mode
content. Use `--reverse` to convert mapped Unicode symbols back to LaTeX
macros.

```powershell
python -m latex-toolkit.commands.tex2uni .\paper.tex
python -m latex-toolkit.commands.tex2uni .\paper.tex --reverse
python -m latex-toolkit.commands.tex2uni .\paper.tex -o .\paper.unicode.tex
```

### `uni2tex`

Runs the reverse-direction conversion from mapped Unicode math symbols back to
LaTeX macros.

```powershell
python -m latex-toolkit.commands.uni2tex .\paper.tex
python -m latex-toolkit.commands.uni2tex .\paper.tex -o .\paper.ascii.tex
```

### `aligned2baea`

Compresses exact `\begin{aligned}[t] ... \end{aligned}` blocks into the local
`\ba ... \ea` shorthand. Use `--reverse` to expand the shorthand back to
explicit `aligned` environments.

```powershell
python -m latex-toolkit.commands.aligned2baea .\paper.tex
python -m latex-toolkit.commands.aligned2baea .\paper.tex --reverse
python -m latex-toolkit.commands.aligned2baea .\paper.tex -o .\paper.converted.tex
```

### `baea2aligned`

Runs the reverse-direction conversion from `\ba` / `\ea` back to explicit
`aligned` environments.

```powershell
python -m latex-toolkit.commands.baea2aligned .\paper.tex
python -m latex-toolkit.commands.baea2aligned .\paper.tex -o .\paper.expanded.tex
```

### `ltae2aligned`

Rewrites `\begin{ltae} ... \end{ltae}` environments as
`\begin{aligned}[t] ... \end{aligned}` blocks and prefixes top-level rows with
`&`. Nested environments such as `cases` keep their own row structure.

```powershell
python -m latex-toolkit.commands.ltae2aligned .\paper.tex
python -m latex-toolkit.commands.ltae2aligned .\paper.tex -o .\paper.converted.tex
```

### `eqn-star2dmath`

Rewrites `equation*` environments as plain `\[ ... \]` display math. Use
`--reverse` to rewrite plain display math back to `equation*`; standalone
`\eqnum` blocks are left untouched.

```powershell
python -m latex-toolkit.commands.eqn-star2dmath .\paper.tex
python -m latex-toolkit.commands.eqn-star2dmath .\paper.tex --reverse
python -m latex-toolkit.commands.eqn-star2dmath .\paper.tex -o .\paper.converted.tex
```

### `dmath2eqn-star`

Runs the reverse-direction conversion from plain `\[ ... \]` display math back
to `equation*` environments.

```powershell
python -m latex-toolkit.commands.dmath2eqn-star .\paper.tex
python -m latex-toolkit.commands.dmath2eqn-star .\paper.tex -o .\paper.converted.tex
```

### `eqn2dmath-eqnum`

Rewrites `equation` environments as `\[\eqnum ... \]` numbered-display blocks.
Use `--reverse` to rewrite only standalone `\eqnum`-prefixed display math back
to `equation`.

```powershell
python -m latex-toolkit.commands.eqn2dmath-eqnum .\paper.tex
python -m latex-toolkit.commands.eqn2dmath-eqnum .\paper.tex --reverse
python -m latex-toolkit.commands.eqn2dmath-eqnum .\paper.tex -o .\paper.converted.tex
```

### `dmath-eqnum2eqn`

Runs the reverse-direction conversion from `\[\eqnum ... \]` display math back
to `equation` environments.

```powershell
python -m latex-toolkit.commands.dmath-eqnum2eqn .\paper.tex
python -m latex-toolkit.commands.dmath-eqnum2eqn .\paper.tex -o .\paper.converted.tex
```
