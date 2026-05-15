# eqn-star2dmath

`eqn-star2dmath` converts between explicit `equation*` environments and plain
`\[ ... \]` display math.

## Usage

```bash
python -m latex_toolkit.commands.eqn_star2dmath paper.tex
python -m latex_toolkit.commands.eqn_star2dmath paper.tex --reverse
python -m latex_toolkit.commands.eqn_star2dmath paper.tex -o paper.converted.tex
python -m latex_toolkit.commands.eqn_star2dmath paper.tex -B
```

## Notes

- By default, the command overwrites the input file.
- Use `-o/--output` to write the converted document to a different path.
- A timestamped backup is created in `.backup` through `lib.backup.backup_file()` before overwriting unless `-B/--no-backup` is supplied.
- Forward conversion rewrites balanced `equation*` environments as exact `\[ ... \]` blocks.
- Reverse conversion rewrites only plain display math and leaves standalone `\eqnum`-prefixed blocks untouched.
- When a balanced `document` environment is present, only the document body is rewritten.
