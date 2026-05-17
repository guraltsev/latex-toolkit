# `tm_alignedt2ltae`

`tm_alignedt2ltae` rewrites strict TeXmacs `<aligned|t|...>` tables as
`<ltae|...>` tables when the table shape can be converted without changing
ambiguous source.

## Use Cases

- Normalize copied TeXmacs markup before converting it to LaTeX.
- Collapse strict top-aligned two-column TeXmacs tables into the local `ltae`
  representation.

## Usage

```powershell
python -m latex_toolkit.commands.tm_alignedt2ltae .\paper.tm
python -m latex_toolkit.commands.tm_alignedt2ltae .\paper.tm -o .\paper.converted.tm
python -m latex_toolkit.commands.tm_alignedt2ltae --clipboard
```

The command supports file mode and clipboard mode for TeXmacs source text.

## Options

| Option | Meaning |
| --- | --- |
| `input` | Optional TeXmacs source path in file mode. Required unless `--clipboard` is used. |
| `--clipboard` | Read TeXmacs markup from the system clipboard and replace the clipboard with converted text. It rejects simultaneous input or output paths. |
| `-o`, `--output`, `--output-file` | Write converted text to a separate path without changing the source file or creating a backup. |
| `-B`, `--no-backup` | Skip backup creation when overwriting the input file. |
| `--backup-dir` | Backup directory used only when overwriting the input. Defaults to `.backup`. |

## Examples

Input:

```text
<aligned|t|<tformat|<table|<row|<cell|>|<cell|x>>>>>
```

Output:

```text
<ltae|<tformat|<table|<row|<cell|x>>>>>
```

## Behavior Notes

- By default, file mode overwrites the input after creating a timestamped
  backup under `.backup`.
- The command converts only `<aligned|t|<tformat|<table|...>>>` constructs.
- Every row must have exactly two cells. The first cell must be empty, except
  for the supported shape where only the first row's first cell has payload and
  that payload can be hoisted before the converted table.
- Nested strict tables are converted wherever they appear.
- Non-top-aligned, malformed, escaped, or non-strict TeXmacs constructs are
  preserved.

## Python API

Use `latex_toolkit.commands.tm_alignedt2ltae.main.transform_text(text)` to
convert raw TeXmacs markup.

## Related Commands

- `tm2tm` runs this command as its clipboard normalization step.
