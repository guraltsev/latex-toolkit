# list-graphics

`list-graphics` prints the targets of `\includegraphics{...}` commands.

## Usage

```bash
lt-cli list-graphics thesis.tex
lt-cli list-graphics thesis.tex --unique
lt-cli list-graphics thesis.tex --with-source
lt-cli list-graphics thesis.tex --no-recursive
```

## Notes

- By default, it scans the root file and recursively included `\input`, `\include`, `\subfile`, and `\subfileinclude` sources.
- Graphics directives inside `%` comments are ignored.
- This is a read-only command and opts out of the write-policy tests with `OVERWRITES_SOURCE_TEX = False`.
