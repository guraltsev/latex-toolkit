# tmscript2substack

`tmscript2substack` rewrites TeXmacs centered script arrays to explicit
`\substack{...}` calls.

## Usage

```bash
python -m latex-toolkit.commands.tmscript2substack paper.tex
python -m latex-toolkit.commands.tmscript2substack paper.tex -o paper.converted.tex
python -m latex-toolkit.commands.tmscript2substack paper.tex -B
```

## Notes

- By default, the command overwrites the input file.
- Use `-o/--output` to write the converted document to a different path.
- A timestamped backup is created in `.backup` through `lib.backup.backup_file()` before overwriting unless `-B/--no-backup` is supplied.
- Only `\tmscript{\begin{array}{c} ... \end{array}}` is converted.
- When a balanced `document` environment is present, only the document body is rewritten.
