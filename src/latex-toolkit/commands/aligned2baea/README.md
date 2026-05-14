# aligned2baea

`aligned2baea` converts between explicit `aligned` environments and the local
`\ba` / `\ea` shorthand.

## Usage

```bash
python -m latex-toolkit.commands.aligned2baea paper.tex
python -m latex-toolkit.commands.aligned2baea paper.tex --reverse
python -m latex-toolkit.commands.aligned2baea paper.tex -o paper.converted.tex
python -m latex-toolkit.commands.aligned2baea paper.tex -B
```

## Notes

- By default, the command overwrites the input file.
- Use `-o/--output` to write the converted document to a different path.
- A timestamped backup is created in `.backup` through `lib.backup.backup_file()` before overwriting unless `-B/--no-backup` is supplied.
- Forward conversion only compresses exact `\begin{aligned}[t] ... \end{aligned}` blocks.
- Reverse conversion preserves comments and only expands literal `\ba` and `\ea` control words.
- When a balanced `document` environment is present, only the document body is rewritten.
