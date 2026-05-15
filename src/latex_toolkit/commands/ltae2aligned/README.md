# ltae2aligned

`ltae2aligned` rewrites `\begin{ltae} ... \end{ltae}` environments as explicit
`\begin{aligned}[t] ... \end{aligned}` blocks and adds a leading `&` to each
top-level row.

## Usage

```bash
python -m latex_toolkit.commands.ltae2aligned paper.tex
python -m latex_toolkit.commands.ltae2aligned paper.tex -o paper.converted.tex
python -m latex_toolkit.commands.ltae2aligned paper.tex -B
```

## Notes

- By default, the command overwrites the input file.
- Use `-o/--output` to write the converted document to a different path.
- A timestamped backup is created in `.backup` before overwriting unless `-B/--no-backup` is supplied.
- Row markers are added only after top-level `\\` row separators.
- Nested environments such as `cases` are preserved without adding `&` to their rows.
- When a balanced `document` environment is present, only the document body is rewritten.
