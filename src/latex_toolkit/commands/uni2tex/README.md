# uni2tex

`uni2tex` is the reverse-direction companion to `tex2uni`. It converts a small
mapped set of Unicode math symbols back to LaTeX macros.

## Usage

```bash
python -m latex_toolkit.commands.uni2tex paper.tex
python -m latex_toolkit.commands.uni2tex paper.tex -o paper.ascii.tex
python -m latex_toolkit.commands.uni2tex paper.tex -B
```

## Notes

- This command delegates to `tex2uni --reverse`.
- By default, the command overwrites the input file.
- Use `-o/--output` to write the converted document to a different path.
- A timestamped backup is created in `.backup` before overwriting unless `-B/--no-backup` is supplied.
- Conversion only affects mutable math-mode content.
- `%` comments are preserved verbatim.
- When a balanced `document` environment is present, only the document body is rewritten.
