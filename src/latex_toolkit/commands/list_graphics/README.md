# `list_graphics`

`list_graphics` reports `\includegraphics{...}` targets from LaTeX source. It
prints a newline-delimited report instead of rewriting files. Its historical
help and log label is `list-graphics`.

## Use Cases

- Audit the image files referenced by a paper or thesis.
- Replace clipboard source with a quick graphics-target report.

## Usage

```powershell
python -m latex_toolkit.commands.list_graphics .\thesis.tex
python -m latex_toolkit.commands.list_graphics .\thesis.tex --unique
python -m latex_toolkit.commands.list_graphics .\thesis.tex --with-source
python -m latex_toolkit.commands.list_graphics --clipboard --with-source
```

The command supports read-only file reporting and clipboard reporting. It does
not expose output-file or backup options.

## Options

| Option | Meaning |
| --- | --- |
| `input` | Optional root `.tex` path in file mode. Required unless `--clipboard` is used. |
| `--clipboard` | Read LaTeX from the system clipboard and replace the clipboard with the rendered report. It rejects an input path. |
| `--no-recursive` | Inspect only the root file instead of walking supported include commands. |
| `--unique` | Emit each rendered report line only once. |
| `--with-source` | Prefix each target with the source file path. Clipboard mode uses `<clipboard>`. |

## Examples

Input:

```tex
\includegraphics[width=.5\textwidth]{figures/plot}
% \includegraphics{draft-only}
```

Standard output:

```text
figures/plot
```

With `--with-source` in clipboard mode:

```text
<clipboard>: figures/plot
```

## Behavior Notes

- File mode prints to standard output and never rewrites TeX files.
- By default, file mode scans the root and recursively included `\input`,
  `\include`, `\subfile`, and `\subfileinclude` sources.
- Graphics directives inside `%` comments are ignored.
- Targets are reported exactly as written inside the `\includegraphics`
  argument; the command does not resolve image paths or add file extensions.
- Missing include files fail the recursive report.

## Python API

Use `latex_toolkit.commands.list_graphics.main.transform_text(text,
unique=False, with_source=False)` to render a clipboard-style report for raw
text.

## Related Commands

- `expand_includes` uses the same include traversal rules to flatten source.
