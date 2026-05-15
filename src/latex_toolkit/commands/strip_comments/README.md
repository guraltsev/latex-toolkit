# strip-comments

`strip-comments` removes LaTeX `%` comments while preserving escaped percent
signs such as `\%`.

## Usage

```bash
python -m latex_toolkit.commands.strip_comments paper.tex
python -m latex_toolkit.commands.strip_comments paper.tex -o paper.clean.tex
python -m latex_toolkit.commands.strip_comments paper.tex -B
```

## Notes

- By default, the command overwrites the input file.
- Use `-o/--output` to write the cleaned document to a different path.
- A timestamped backup is created in `.backup` through `lib.backup.backup_file()` before overwriting unless `-B/--no-backup` is supplied.
- Line endings stay stable so line numbers remain easier to compare.
- Escaped percent signs (`\%`) are preserved.
- This is not a full TeX lexer; verbatim-like package environments are outside the command's scope.
