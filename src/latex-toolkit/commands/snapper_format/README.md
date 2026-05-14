# snapper_format

`snapper_format` formats LaTeX prose with the `snapper` semantic line break
formatter so emitted prose lines contain at most one sentence.

## Usage

```bash
python -m latex-toolkit.commands.snapper_format paper.tex
python -m latex-toolkit.commands.snapper_format paper.tex -o paper.snapped.tex
python -m latex-toolkit.commands.snapper_format --clipboard
python -m latex-toolkit.commands.snapper_format --install
```

## Notes

- The first formatting run downloads `snapper-fmt` from PyPI into
  `local_lib/snapper-fmt`.
- The command runs the `snapper` executable from that local install directory,
  not from `PATH`.
- By default, the command overwrites the input file after creating a timestamped
  backup in `.backup`.
- Use `--max-width N` to let snapper wrap sentences longer than `N` columns.
  The default, `0`, keeps each sentence on a single line.

