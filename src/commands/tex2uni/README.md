# tex2uni

`tex2uni` converts a small mapped set of LaTeX math macros to Unicode symbols.
With `--reverse`, it converts the same mapped Unicode symbols back to LaTeX
macros.

## Usage

```bash
lt-cli tex2uni paper.tex
lt-cli tex2uni paper.tex --reverse
lt-cli tex2uni paper.tex -o paper.unicode.tex
lt-cli tex2uni paper.tex -B
```

## Notes

- By default, the command overwrites the input file.
- Use `-o/--output` to write the converted document to a different path.
- A UTC backup is created through `lib.backup.backup_file()` before overwriting unless `-B/--no-backup` is supplied.
- Conversion only affects mutable math-mode content.
- `%` comments are preserved verbatim.
- When a balanced `document` environment is present, only the document body is rewritten.
