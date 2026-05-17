# `texmacs_vert_delimiters`

`texmacs_vert_delimiters` rewrites sized double-bar delimiters such as
`\left\|` and `\bigr\|` into explicit `\lVert`, `\rVert`, or `\Vert` delimiter
forms that TeXmacs handles more predictably.

## Use Cases

- Prepare LLM-edited LaTeX containing vertical norm delimiters for TeXmacs.
- Convert side-sensitive delimiter controls without changing comments.

## Usage

```powershell
python -m latex_toolkit.commands.texmacs_vert_delimiters .\paper.tex
python -m latex_toolkit.commands.texmacs_vert_delimiters .\paper.tex -o .\paper.converted.tex
python -m latex_toolkit.commands.texmacs_vert_delimiters --clipboard
```

The command supports file mode and clipboard mode.

## Options

| Option | Meaning |
| --- | --- |
| `input` | Optional `.tex` path in file mode. Required unless `--clipboard` is used. |
| `--clipboard` | Read LaTeX from the system clipboard and replace the clipboard with converted text. It rejects simultaneous input or output paths. |
| `-o`, `--output`, `--output-file` | Write converted text to a separate path without changing the source file or creating a backup. |
| `-B`, `--no-backup` | Skip backup creation when overwriting the input file. |
| `--backup-dir` | Backup directory used only when overwriting the input. Defaults to `.backup`. |

## Examples

Input:

```tex
\left\| x\right\| + \big\| y\big\|
% \left\| comment stays
```

Output:

```tex
\left \lVert x\right \rVert + \big \Vert y\big \Vert
% \left\| comment stays
```

## Behavior Notes

- By default, file mode overwrites the input after creating a timestamped
  backup under `.backup`.
- Left delimiter controls such as `\left`, `\bigl`, and `\Biggl` become
  `\lVert`.
- Right delimiter controls such as `\right`, `\bigr`, and `\Biggr` become
  `\rVert`.
- Neutral delimiter controls such as `\middle`, `\big`, and `\bigm` become
  `\Vert`.
- Comments are preserved by rewriting only the code portion of each line.
- A separating space is added when needed to keep the replacement delimiter
  from merging with a following control-word character.
- When a balanced `document` environment is present, only the document body is
  rewritten.

## Python API

Use `latex_toolkit.commands.texmacs_vert_delimiters.main.transform_text(text)`
to convert raw LaTeX text.

## Related Commands

- `llm_latex_to_texmacs_latex` runs this command after `brace_unary_macros`.
