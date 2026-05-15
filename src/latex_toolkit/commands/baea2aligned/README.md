# baea2aligned

`baea2aligned` is the reverse-direction companion to `aligned2baea`. It expands
literal `\ba` / `\ea` control words into explicit `aligned` environments.

## Usage

```bash
python -m latex_toolkit.commands.baea2aligned paper.tex
python -m latex_toolkit.commands.baea2aligned paper.tex -o paper.expanded.tex
python -m latex_toolkit.commands.baea2aligned paper.tex -B
```

## Notes

- This command delegates to `aligned2baea --reverse`.
- By default, the command overwrites the input file.
- Use `-o/--output` to write the converted document to a different path.
- A timestamped backup is created in `.backup` before overwriting unless `-B/--no-backup` is supplied.
- Comments are preserved verbatim.
- When a balanced `document` environment is present, only the document body is rewritten.
