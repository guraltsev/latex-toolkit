# `delete_macros`

`delete_macros` removes configured unary macro calls together with their
arguments. The default list currently deletes TeXmacs `\hide-preamble{...}`
wrappers.

## Use Cases

- Strip TeXmacs wrapper macros that should not survive into ordinary LaTeX.
- Remove project-local one-argument macros from clipboard text or `.tex` files.

## Usage

```powershell
python -m latex_toolkit.commands.delete_macros .\paper.tex
python -m latex_toolkit.commands.delete_macros .\paper.tex --macros-file C:\path\macros.toml
python -m latex_toolkit.commands.delete_macros --clipboard
```

## Options

| Option | Meaning |
| --- | --- |
| `--clipboard` | Read LaTeX from the clipboard and replace it with converted output. |
| `--macros-file` | Absolute TOML path whose command list replaces the default deleted macro list. |
| `-o`, `--output`, `--output-file` | Write to a separate output path instead of overwriting the input file. |
| `-B`, `--no-backup` | Skip backup creation when overwriting the input file. |
| `--backup-dir` | Backup directory to use when overwriting the input file. |

## Examples

Input:

```tex
\hide-preamble{\usepackage{foo}}
\section{Body}
```

Output:

```tex

\section{Body}
```

## Behavior Notes

- The default deleted macro list contains only `\hide-preamble`.
- Matching macro calls are removed only when a complete unary argument is
  present.
- Braced arguments may contain nested groups and comments.
- A macro file must be an absolute TOML path. A top-level `commands` array is
  required; `macros` is accepted as an alias.

## Python API

Use `latex_toolkit.commands.delete_macros.main.transform_text(text,
commands=None)` to delete matching macro calls from raw text. Pass `commands`
to replace the default deleted macro list.
