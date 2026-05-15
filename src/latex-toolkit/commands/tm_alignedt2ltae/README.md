# tm_alignedt2ltae

`tm_alignedt2ltae` rewrites strict TeXmacs `<aligned|t|...>` tables as
`<ltae|...>` tables. A table is converted only when every row has exactly two
cells and the first column is empty. If only the first row's first cell is
populated, that payload is moved immediately before the converted `ltae`
table.

## Usage

```bash
python -m latex-toolkit.commands.tm_alignedt2ltae paper.tm
python -m latex-toolkit.commands.tm_alignedt2ltae paper.tm -o paper.converted.tm
python -m latex-toolkit.commands.tm_alignedt2ltae --clipboard
```

## Notes

- By default, the command overwrites the input file.
- Use `-o/--output` to write the converted document to a different path.
- A timestamped backup is created in `.backup` before overwriting unless
  `-B/--no-backup` is supplied.
- Nested strict `<aligned|t|...>` tables are converted wherever they appear.
- Non-top-aligned, malformed, or non-strict aligned tables are preserved.
