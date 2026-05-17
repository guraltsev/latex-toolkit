# `brace_unary_macros`

`brace_unary_macros` adds braces around the next unbraced single-token
argument passed to configured unary LaTeX macros, such as rewriting `\bar x`
as `\bar{x}`.

## Use Cases

- Make LLM-edited math safer for tools that expect braced macro arguments.
- Apply a project-specific unary macro list before TeXmacs import.

## Usage

```powershell
python -m latex_toolkit.commands.brace_unary_macros .\paper.tex
python -m latex_toolkit.commands.brace_unary_macros .\paper.tex --macros-file C:\path\macros.toml
python -m latex_toolkit.commands.brace_unary_macros .\paper.tex -o .\paper.braced.tex
python -m latex_toolkit.commands.brace_unary_macros --clipboard
```

The command supports file mode and clipboard mode.

## Options

| Option | Meaning |
| --- | --- |
| `input` | Optional `.tex` path in file mode. Required unless `--clipboard` is used. |
| `--clipboard` | Read LaTeX from the system clipboard and replace the clipboard with converted text. It rejects simultaneous input or output paths. |
| `--macros-file` | Absolute TOML path whose command list replaces the default unary macro list. |
| `-o`, `--output`, `--output-file` | Write converted text to a separate path without changing the source file or creating a backup. |
| `-B`, `--no-backup` | Skip backup creation when overwriting the input file. |
| `--backup-dir` | Backup directory used only when overwriting the input. Defaults to `.backup`. |

## Examples

Input:

```tex
$\bar x + \FT f + \tilde{g}$
```

Output:

```tex
$\bar{x} + \FT{f} + \tilde{g}$
```

Minimal macro configuration:

```toml
commands = ['\FT', '\bar', '\tilde']
```

## Behavior Notes

- By default, file mode overwrites the input after creating a timestamped
  backup under `.backup`.
- The default command list includes `\FT`, `\bar`, `\tilde`, `\dot`, and common
  math accent, font, and decorator macros.
- A macro file must be an absolute TOML path. A top-level `commands` array is
  required; `macros` is accepted as an alias.
- Custom macro files replace the default list rather than extending it. Values
  may include or omit the leading backslash, and duplicates are collapsed in
  first-seen order.
- Already braced arguments, command-definition shapes such as `\FT[1]`, line
  breaks, comments, and structural markers are preserved.
- Only one following token is braced: a control word, a control symbol, or a
  single character.
- Macro configuration is loaded before input files are rewritten or clipboard
  contents are changed.
- When a balanced `document` environment is present, only the document body is
  rewritten.

## Python API

Use `latex_toolkit.commands.brace_unary_macros.main.transform_text(text,
commands=None)` to convert raw text. Pass an iterable of command names to
replace the default list. `latex_toolkit.commands.brace_unary_macros.transform.load_macro_commands(path)`
loads and validates the TOML format used by the CLI.

## Related Commands

- `llm_latex_to_texmacs_latex` runs this command as its first pipeline step.
