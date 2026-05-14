# dollar2bracket

`dollar2bracket` rewrites matched `$...$` and `$$...$$` math delimiters as
`\(...\)` and `\[...\]`. Use `--reverse` to rewrite bracket delimiters back to
dollar delimiters.

## Usage

```bash
python -m latex-toolkit.commands.dollar2bracket paper.tex
python -m latex-toolkit.commands.dollar2bracket paper.tex --reverse
python -m latex-toolkit.commands.dollar2bracket paper.tex -o paper.converted.tex
python -m latex-toolkit.commands.dollar2bracket --clipboard
```

## Notes

- Only matched delimiter pairs are rewritten.
- Escaped dollar signs, comments, and unmatched delimiters are preserved.
- When a balanced `document` environment is present, only the document body is rewritten.
