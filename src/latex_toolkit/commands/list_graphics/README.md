# list-graphics

`list-graphics` prints the targets of `\includegraphics{...}` commands.

## Usage

```bash
python -m latex_toolkit.commands.list_graphics thesis.tex
python -m latex_toolkit.commands.list_graphics thesis.tex --unique
python -m latex_toolkit.commands.list_graphics thesis.tex --with-source
python -m latex_toolkit.commands.list_graphics thesis.tex --no-recursive
```

## Notes

- By default, it scans the root file and recursively included `\input`, `\include`, `\subfile`, and `\subfileinclude` sources.
- Graphics directives inside `%` comments are ignored.
- This is a read-only command: it prints graphics targets and does not rewrite source files.
