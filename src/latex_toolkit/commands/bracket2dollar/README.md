# bracket2dollar

`bracket2dollar` is the reverse-direction companion to `dollar2bracket`. It
rewrites matched `\(...\)` and `\[...\]` math delimiters back to `$...$` and
`$$...$$`.

## Usage

```bash
python -m latex_toolkit.commands.bracket2dollar paper.tex
python -m latex_toolkit.commands.bracket2dollar paper.tex -o paper.converted.tex
python -m latex_toolkit.commands.bracket2dollar --clipboard
```

## Notes

- This command delegates to `dollar2bracket --reverse`.
- Only matched delimiter pairs are rewritten.
- Linebreak options such as `\\[0.5em]` are preserved.
