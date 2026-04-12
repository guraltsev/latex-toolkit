# strip-comments

`strip-comments` removes LaTeX `%` comments while preserving escaped percent
signs such as `\\%`.

## Usage

```bash
lt-cli strip-comments paper.tex
lt-cli strip-comments paper.tex -o paper.clean.tex
lt-cli strip-comments paper.tex --in-place
lt-cli strip-comments paper.tex --in-place -B
```

## Notes

- Keeps line endings stable so line numbers stay easier to compare.
- Ignores escaped percent signs (`\\%`).
- Not a full TeX lexer; constructs such as verbatim-like package environments are outside this command's scope.
- When overwriting a file, it creates a UTC backup through `lib.backup.backup_file()` unless `-B/--no-backup` is supplied.
