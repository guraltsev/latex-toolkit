# `strip_comments`

`strip_comments` removes unescaped LaTeX percent comments from `.tex` source
while preserving escaped percent signs such as `\%`. Its historical help and
log label is `strip-comments`.

## Use Cases

- Clean draft-only `%` comments out of a source file before sharing it.
- Normalize clipboard text without changing escaped percent literals.

## Usage

```powershell
python -m latex_toolkit.commands.strip_comments .\paper.tex
python -m latex_toolkit.commands.strip_comments .\paper.tex -o .\paper.clean.tex
python -m latex_toolkit.commands.strip_comments --clipboard
```

The command supports file mode and clipboard mode.

## Options

| Option | Meaning |
| --- | --- |
| `input` | Optional `.tex` path in file mode. Required unless `--clipboard` is used. |
| `--clipboard` | Read LaTeX from the system clipboard and replace the clipboard with stripped text. It rejects simultaneous input or output paths. |
| `-o`, `--output`, `--output-file` | Write stripped text to a separate path without changing the source file or creating a backup. |
| `-B`, `--no-backup` | Skip backup creation when overwriting the input file. |
| `--backup-dir` | Backup directory used only when overwriting the input. Defaults to `.backup`. |

## Examples

Input:

```tex
Value \% stays% remove this comment
Next line
```

Output:

```tex
Value \% stays
Next line
```

## Behavior Notes

- By default, file mode overwrites the input after creating a timestamped
  backup under `.backup`.
- Original line endings are preserved when a comment body is removed.
- A percent sign starts a comment only when it is not escaped by a preceding
  backslash sequence.
- The command is a lightweight text transform, not a complete TeX lexer;
  verbatim-like package environments are outside its scope.

## Python API

Use `latex_toolkit.commands.strip_comments.main.transform_text(text)` to strip
raw text without reading files or touching the clipboard.

## Related Commands

- `expand_includes` can flatten a cleaned source tree.
- `list_graphics` uses the same comment-splitting behavior when reporting
  graphics targets.
