# expand-includes

`expand-includes` flattens a LaTeX document by recursively expanding
`\\input{...}` and `\\include{...}` references.

## Usage

```bash
lt-cli expand-includes main.tex
lt-cli expand-includes main.tex -o flat.tex
lt-cli expand-includes main.tex --in-place
lt-cli expand-includes main.tex --in-place -B
```

## Notes

- Handles common `\\input{...}` and `\\include{...}` patterns.
- Ignores include directives that are inside `%` comments.
- Does not attempt full macro expansion.
- When overwriting a file, it creates a UTC backup through `lib.backup.backup_file()` unless `-B/--no-backup` is supplied.
- The same `from lib...` imports work when this folder is extracted into a standalone command directory with a sibling `lib/`.
