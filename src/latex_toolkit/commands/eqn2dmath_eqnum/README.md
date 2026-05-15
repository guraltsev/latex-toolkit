# eqn2dmath-eqnum

`eqn2dmath-eqnum` converts between explicit `equation` environments and the
project's `\[\eqnum ... \]` numbered-display convention.

## Usage

```bash
python -m latex_toolkit.commands.eqn2dmath_eqnum paper.tex
python -m latex_toolkit.commands.eqn2dmath_eqnum paper.tex --reverse
python -m latex_toolkit.commands.eqn2dmath_eqnum paper.tex -o paper.converted.tex
python -m latex_toolkit.commands.eqn2dmath_eqnum paper.tex -B
```

## Notes

- By default, the command overwrites the input file.
- Use `-o/--output` to write the converted document to a different path.
- A timestamped backup is created in `.backup` before overwriting unless `-B/--no-backup` is supplied.
- Forward conversion rewrites balanced `equation` environments as exact `\[\eqnum ... \]` blocks.
- Reverse conversion rewrites only display-math blocks whose body begins with a standalone `\eqnum` control word.
- When a balanced `document` environment is present, only the document body is rewritten.
