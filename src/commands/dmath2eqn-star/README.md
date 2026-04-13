# dmath2eqn-star

`dmath2eqn-star` is the reverse-direction companion to `eqn-star2dmath`. It
rewrites plain `\[ ... \]` display math as `equation*` environments.

## Usage

```bash
lt-cli dmath2eqn-star paper.tex
lt-cli dmath2eqn-star paper.tex -o paper.converted.tex
lt-cli dmath2eqn-star paper.tex -B
```

## Notes

- This command delegates to `eqn-star2dmath --reverse`.
- By default, the command overwrites the input file.
- Use `-o/--output` to write the converted document to a different path.
- A UTC backup is created through `lib.backup.backup_file()` before overwriting unless `-B/--no-backup` is supplied.
- Standalone `\eqnum`-prefixed display math is intentionally left for the numbered-equation workflow.
- When a balanced `document` environment is present, only the document body is rewritten.
