# expand-includes

`expand-includes` flattens a LaTeX document by recursively expanding
`\input{...}`, `\include{...}`, `\subfile{...}`, and
`\subfileinclude{...}` references.

## Usage

```bash
lt-cli expand-includes main.tex
lt-cli expand-includes main.tex -o flat.tex
lt-cli expand-includes main.tex -B
```

## Notes

- By default, the command overwrites the input file.
- Use `-o/--output` to write the flattened document to a different path.
- A UTC backup is created through `lib.backup.backup_file()` before overwriting unless `-B/--no-backup` is supplied.
- Include directives inside `%` comments are ignored.
- `\subfile{...}` and `\subfileinclude{...}` are handled using the `subfiles` package inclusion rules.
- The same `from lib...` imports work when this folder is extracted into a standalone command directory with a sibling `lib/`.
