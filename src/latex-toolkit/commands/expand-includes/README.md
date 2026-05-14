# expand-includes

`expand-includes` flattens a LaTeX document by recursively expanding
`\input{...}`, `\include{...}`, `\subfile{...}`, and
`\subfileinclude{...}` references.

## Usage

```bash
python -m latex-toolkit.commands.expand-includes main.tex
python -m latex-toolkit.commands.expand-includes main.tex -o flat.tex
python -m latex-toolkit.commands.expand-includes main.tex -B
```

## Notes

- By default, the command overwrites the input file.
- Use `-o/--output` to write the flattened document to a different path.
- A timestamped backup is created in `.backup` through `lib.backup.backup_file()` before overwriting unless `-B/--no-backup` is supplied.
- Include directives inside `%` comments are ignored.
- `\subfile{...}` and `\subfileinclude{...}` are handled using the `subfiles` package inclusion rules.
- The same `from lib...` imports work when this folder is extracted into a standalone command directory with a sibling `lib/`.
