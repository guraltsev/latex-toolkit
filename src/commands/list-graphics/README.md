# list-graphics

`list-graphics` prints the targets of `\\includegraphics{...}` commands.

## Usage

```bash
lt-cli list-graphics thesis.tex
lt-cli list-graphics thesis.tex --unique
lt-cli list-graphics thesis.tex --with-source
lt-cli list-graphics thesis.tex --no-recursive
```

## Notes

- By default, scans the root file and recursively included `\\input` / `\\include` files.
- Ignores graphics directives that appear inside `%` comments.
- This is a read-only command and does not need backup handling.
