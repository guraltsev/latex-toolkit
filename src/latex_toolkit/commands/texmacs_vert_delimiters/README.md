# texmacs_vert_delimiters

`texmacs_vert_delimiters` rewrites sized `\|` delimiters to explicit
`\lVert`, `\rVert`, or `\Vert` delimiters for TeXmacs-friendly LaTeX.

## Usage

```bash
python -m latex_toolkit.commands.texmacs_vert_delimiters paper.tex
python -m latex_toolkit.commands.texmacs_vert_delimiters paper.tex -o paper.converted.tex
python -m latex_toolkit.commands.texmacs_vert_delimiters --clipboard
```

## Notes

- By default, the command overwrites the input file.
- Use `-o/--output` to write the converted document to a different path.
- A timestamped backup is created in `.backup` through `lib.backup.backup_file()` before overwriting unless `-B/--no-backup` is supplied.
- Left delimiter controls such as `\left`, `\bigl`, and `\Biggl` become `\lVert`.
- Right delimiter controls such as `\right`, `\bigr`, and `\Biggr` become `\rVert`.
- Neutral delimiter controls such as `\middle`, `\big`, and `\bigm` become `\Vert`.
- When a balanced `document` environment is present, only the document body is rewritten.
