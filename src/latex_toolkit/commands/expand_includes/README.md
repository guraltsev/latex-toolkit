# `expand_includes`

`expand_includes` flattens a LaTeX source tree by replacing supported include
commands with the contents of the referenced `.tex` files. Its historical help
and log label is `expand-includes`.

## Use Cases

- Produce a single-file version of a multi-file paper.
- Flatten a `subfiles` project before passing source to another tool.

## Usage

```powershell
python -m latex_toolkit.commands.expand_includes .\main.tex
python -m latex_toolkit.commands.expand_includes .\main.tex -o .\flat.tex
python -m latex_toolkit.commands.expand_includes --clipboard
```

The command supports file mode and clipboard mode. Clipboard include paths are
resolved from the current working directory.

## Options

| Option | Meaning |
| --- | --- |
| `input` | Optional root `.tex` path in file mode. Required unless `--clipboard` is used. |
| `--clipboard` | Read LaTeX from the system clipboard and replace the clipboard with expanded text. It rejects simultaneous input or output paths. |
| `-o`, `--output`, `--output-file` | Write flattened text to a separate path without changing the source file or creating a backup. |
| `-B`, `--no-backup` | Skip backup creation when overwriting the input file. |
| `--backup-dir` | Backup directory used only when overwriting the input. Defaults to `.backup`. |

## Examples

`main.tex`:

```tex
Intro.
\input{sections/result}
Done.
```

`sections/result.tex`:

```tex
Result text.
```

Flattened output:

```tex
Intro.
Result text.
Done.
```

## Behavior Notes

- By default, file mode overwrites the input after creating a timestamped
  backup under `.backup`.
- The supported include commands are `\input`, `\include`, `\subfile`, and
  `\subfileinclude`.
- Include targets are resolved relative to the file that names them; suffixless
  targets are tried as written and with `.tex` appended.
- Include directives inside `%` comments are ignored.
- `subfiles` children contribute only their document body when
  `\begin{document}` and `\end{document}` are recognizable.
- Missing include files, empty targets, and include cycles fail before output
  is written.

## Python API

Use `latex_toolkit.commands.expand_includes.main.transform_text(text,
base_dir=...)` for raw text. `base_dir` controls how relative include targets
are resolved.

## Related Commands

- `strip_comments` removes comments before or after flattening.
- `list_graphics` walks the same include forms for reporting graphics.
