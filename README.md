# latex-toolkit

`latex-toolkit` is a small collection of Python commands for editing LaTeX
source files. It is meant to be run directly from this source checkout.

## Running Without Installation

The package is not assumed to be installed. From the repository root, put the
local `src` directory on `PYTHONPATH` for the current PowerShell session:

```powershell
$env:PYTHONPATH = (Resolve-Path .\src).Path
python -m latex_toolkit.commands.strip_comments .\paper.tex
```

You can also run from `src` directly because Python automatically puts the
current directory on the module search path:

```powershell
cd path\to\latex-toolkit\src
python -m latex_toolkit.commands.strip_comments ..\paper.tex
```

Use absolute paths or paths relative to your current working directory for TeX
files and output files.

## Command Pattern

Every command can run as a Python package without naming its `main` module:

```powershell
python -m latex_toolkit.commands.<command_name> <input.tex> [options]
```

Python module names use underscores because they are importable package names:

```powershell
python -m latex_toolkit.commands.eqn_star2dmath .\paper.tex
python -m latex_toolkit.commands.eqn2dmath_eqnum .\paper.tex --reverse
```

Some commands still print historical dash spellings such as `strip-comments`
in help text and log messages; those are command labels, not Python module
paths.

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
python -m latex_toolkit.commands.expand_includes .\main.tex --output-file .\flat.tex
```

Use `-B` or `--no-backup` only when overwriting the input file without creating
a backup is intentional.

## Clipboard Mode

Commands also support `--clipboard`. In clipboard mode, the command reads text
from the system clipboard and replaces the clipboard contents with the result.
Do not pass input or output paths with `--clipboard`.

```powershell
python -m latex_toolkit.commands.tex2uni --clipboard
```

## Commands

### `strip-comments`

Removes LaTeX `%` comments while preserving escaped percent signs such as `\%`.

```powershell
python -m latex_toolkit.commands.strip_comments .\paper.tex
python -m latex_toolkit.commands.strip_comments .\paper.tex -o .\paper.clean.tex
```

### `expand-includes`

Flattens a document by recursively expanding `\input{...}`, `\include{...}`,
`\subfile{...}`, and `\subfileinclude{...}` references.

```powershell
python -m latex_toolkit.commands.expand_includes .\main.tex
python -m latex_toolkit.commands.expand_includes .\main.tex --output-file .\flat.tex
```

### `list-graphics`

Lists `\includegraphics{...}` targets, optionally across recursively included
source files. This command prints to standard output and does not overwrite TeX
files.

```powershell
python -m latex_toolkit.commands.list_graphics .\thesis.tex
python -m latex_toolkit.commands.list_graphics .\thesis.tex --unique
python -m latex_toolkit.commands.list_graphics .\thesis.tex --with-source
python -m latex_toolkit.commands.list_graphics .\thesis.tex --no-recursive
```

### `tex2uni`

Converts mapped LaTeX math macros to Unicode symbols inside mutable math-mode
content. Use `--reverse` to convert mapped Unicode symbols back to LaTeX
macros.

```powershell
python -m latex_toolkit.commands.tex2uni .\paper.tex
python -m latex_toolkit.commands.tex2uni .\paper.tex --reverse
python -m latex_toolkit.commands.tex2uni .\paper.tex -o .\paper.unicode.tex
```

### `uni2tex`

Runs the reverse-direction conversion from mapped Unicode math symbols back to
LaTeX macros.

```powershell
python -m latex_toolkit.commands.uni2tex .\paper.tex
python -m latex_toolkit.commands.uni2tex .\paper.tex -o .\paper.ascii.tex
```

### `dollar2bracket`

Rewrites matched `$...$` and `$$...$$` math delimiters as `\(...\)` and
`\[...\]`. Use `--reverse` to convert bracket delimiters back to dollar
delimiters. Comments, escaped dollar signs, and unmatched delimiters are
preserved.

```powershell
python -m latex_toolkit.commands.dollar2bracket .\paper.tex
python -m latex_toolkit.commands.dollar2bracket .\paper.tex --reverse
python -m latex_toolkit.commands.dollar2bracket .\paper.tex -o .\paper.converted.tex
```

### `bracket2dollar`

Runs the reverse-direction conversion from `\(...\)` and `\[...\]` back to
`$...$` and `$$...$$`.

```powershell
python -m latex_toolkit.commands.bracket2dollar .\paper.tex
python -m latex_toolkit.commands.bracket2dollar .\paper.tex -o .\paper.converted.tex
```

### `aligned2baea`

Compresses exact `\begin{aligned}[t] ... \end{aligned}` blocks into the local
`\ba ... \ea` shorthand. Use `--reverse` to expand the shorthand back to
explicit `aligned` environments.

```powershell
python -m latex_toolkit.commands.aligned2baea .\paper.tex
python -m latex_toolkit.commands.aligned2baea .\paper.tex --reverse
python -m latex_toolkit.commands.aligned2baea .\paper.tex -o .\paper.converted.tex
```

### `baea2aligned`

Runs the reverse-direction conversion from `\ba` / `\ea` back to explicit
`aligned` environments.

```powershell
python -m latex_toolkit.commands.baea2aligned .\paper.tex
python -m latex_toolkit.commands.baea2aligned .\paper.tex -o .\paper.expanded.tex
```

### `ltae2aligned`

Rewrites `\begin{ltae} ... \end{ltae}` environments as
`\begin{aligned}[t] ... \end{aligned}` blocks and prefixes top-level rows with
`&`. Nested environments such as `cases` keep their own row structure.

```powershell
python -m latex_toolkit.commands.ltae2aligned .\paper.tex
python -m latex_toolkit.commands.ltae2aligned .\paper.tex -o .\paper.converted.tex
```

### `tmscript2substack`

Rewrites TeXmacs `\tmscript{\begin{array}{c} ... \end{array}}` constructs as
`\substack{...}`.

```powershell
python -m latex_toolkit.commands.tmscript2substack .\paper.tex
python -m latex_toolkit.commands.tmscript2substack .\paper.tex -o .\paper.converted.tex
```

### `tm_alignedt2ltae`

Rewrites strict TeXmacs `<aligned|t|...>` tables as `<ltae|...>` tables. A
table is converted only when every row has exactly two cells and the first
cell is empty.

```powershell
python -m latex_toolkit.commands.tm_alignedt2ltae .\paper.tm
python -m latex_toolkit.commands.tm_alignedt2ltae .\paper.tm -o .\paper.converted.tm
python -m latex_toolkit.commands.tm_alignedt2ltae --clipboard
```

### `tm2tm`

Runs a clipboard normalization pipeline for TeXmacs snippets:
`tm_alignedt2ltae`.

```powershell
python -m latex_toolkit.commands.tm2tm
.\tm2tm.cmd
```

### `proofstar2proof`

Rewrites TeXmacs `\begin{proof*}{Title} ... \end{proof*}` environments as
`\begin{proof}[Title] ... \end{proof}` environments. Use `--reverse` to rewrite
titled `proof` environments back to TeXmacs `proof*` environments.

```powershell
python -m latex_toolkit.commands.proofstar2proof .\paper.tex
python -m latex_toolkit.commands.proofstar2proof .\paper.tex --reverse
python -m latex_toolkit.commands.proofstar2proof .\paper.tex -o .\paper.converted.tex
```

### `proof2proofstar`

Runs the reverse-direction conversion from
`\begin{proof}[Title] ... \end{proof}` back to
`\begin{proof*}{Title} ... \end{proof*}`.

```powershell
python -m latex_toolkit.commands.proof2proofstar .\paper.tex
python -m latex_toolkit.commands.proof2proofstar .\paper.tex -o .\paper.converted.tex
```

### `brace_unary_macros`

Adds braces around the next unbraced token passed to configured unary macros.
The default list includes `\FT`, `\bar`, `\tilde`, `\dot`, and common math
accent variants.

```powershell
python -m latex_toolkit.commands.brace_unary_macros .\paper.tex
python -m latex_toolkit.commands.brace_unary_macros .\paper.tex --macros-file C:\path\macros.toml
```

Custom TOML files replace the default list and use a top-level `commands`
array. Use TOML literal strings to avoid escaping backslashes:

```toml
commands = ['\FT', '\bar', '\tilde']
```

### `texmacs_vert_delimiters`

Rewrites sized `\|` delimiters to explicit TeXmacs-friendly delimiter commands:
`\left\|` becomes `\left \lVert`, `\right\|` becomes `\right \rVert`, and
size variants such as `\bigl\|`, `\Bigl\|`, and `\bigr\|` follow the same
left/right convention.

```powershell
python -m latex_toolkit.commands.texmacs_vert_delimiters .\paper.tex
python -m latex_toolkit.commands.texmacs_vert_delimiters .\paper.tex -o .\paper.converted.tex
python -m latex_toolkit.commands.texmacs_vert_delimiters --clipboard
```

### `texmacs_latex_to_llm_latex`

Runs a clipboard pipeline for TeXmacs-generated LaTeX: `dollar2bracket`,
`ltae2aligned`, `tmscript2substack`, `proofstar2proof`, then `uni2tex`.

```powershell
python -m latex_toolkit.commands.texmacs_latex_to_llm_latex
.\texmacs_latex_to_llm_latex.cmd
```

### `llm_latex_to_texmacs_latex`

Runs a clipboard conversion for LLM-friendly LaTeX headed back to TeXmacs:
`brace_unary_macros`, `texmacs_vert_delimiters`, then `proof2proofstar`.

```powershell
python -m latex_toolkit.commands.llm_latex_to_texmacs_latex
python -m latex_toolkit.commands.llm_latex_to_texmacs_latex --macros-file C:\path\macros.toml
.\llm_latex_to_texmacs_latex.cmd
.\llm_latex_to_texmacs_latex.cmd --macros-file C:\path\macros.toml
```

### `snapper_format`

Formats LaTeX prose with the external `snapper` semantic line break formatter
so each emitted prose line contains at most one sentence. The first formatting
run downloads `snapper-fmt` into `src/latex_toolkit/lib/snapper-fmt`; that
directory is kept in git with `README.md`, while the installed runtime is
ignored.

```powershell
python -m latex_toolkit.commands.snapper_format .\paper.tex
python -m latex_toolkit.commands.snapper_format .\paper.tex -o .\paper.snapped.tex
python -m latex_toolkit.commands.snapper_format --clipboard
.\snapper_format.cmd .\paper.tex
```

### `eqn-star2dmath`

Rewrites `equation*` environments as plain `\[ ... \]` display math. Use
`--reverse` to rewrite plain display math back to `equation*`; standalone
`\eqnum` blocks are left untouched.

```powershell
python -m latex_toolkit.commands.eqn_star2dmath .\paper.tex
python -m latex_toolkit.commands.eqn_star2dmath .\paper.tex --reverse
python -m latex_toolkit.commands.eqn_star2dmath .\paper.tex -o .\paper.converted.tex
```

### `dmath2eqn-star`

Runs the reverse-direction conversion from plain `\[ ... \]` display math back
to `equation*` environments.

```powershell
python -m latex_toolkit.commands.dmath2eqn_star .\paper.tex
python -m latex_toolkit.commands.dmath2eqn_star .\paper.tex -o .\paper.converted.tex
```

### `eqn2dmath-eqnum`

Rewrites `equation` environments as `\[\eqnum ... \]` numbered-display blocks.
Use `--reverse` to rewrite only standalone `\eqnum`-prefixed display math back
to `equation`.

```powershell
python -m latex_toolkit.commands.eqn2dmath_eqnum .\paper.tex
python -m latex_toolkit.commands.eqn2dmath_eqnum .\paper.tex --reverse
python -m latex_toolkit.commands.eqn2dmath_eqnum .\paper.tex -o .\paper.converted.tex
```

### `dmath-eqnum2eqn`

Runs the reverse-direction conversion from `\[\eqnum ... \]` display math back
to `equation` environments.

```powershell
python -m latex_toolkit.commands.dmath_eqnum2eqn .\paper.tex
python -m latex_toolkit.commands.dmath_eqnum2eqn .\paper.tex -o .\paper.converted.tex
```
