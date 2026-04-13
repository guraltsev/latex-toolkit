# dmath-eqnum2eqn

`dmath-eqnum2eqn` is the reverse-direction companion to `eqn2dmath-eqnum`. It
rewrites `\[\eqnum ... \]` blocks as `equation` environments.

## Usage

```bash
lt-cli dmath-eqnum2eqn paper.tex
lt-cli dmath-eqnum2eqn paper.tex -o paper.converted.tex
lt-cli dmath-eqnum2eqn paper.tex -B
```

## Notes

- This command delegates to `eqn2dmath-eqnum --reverse`.
- By default, the command overwrites the input file.
- Use `-o/--output` to write the converted document to a different path.
- A UTC backup is created through `lib.backup.backup_file()` before overwriting unless `-B/--no-backup` is supplied.
- Plain `\[ ... \]` display-math blocks are intentionally left untouched.
- When a balanced `document` environment is present, only the document body is rewritten.
