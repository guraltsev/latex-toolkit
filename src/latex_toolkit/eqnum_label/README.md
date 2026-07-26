# eqnum_label

Normalize display-math label placement, with or without `\eqnum`. The command
always writes one space in an adjacent `\eqnum\label{...}` pair. In `\[...]`,
`equation`, and `equation*` displays, one label moves to the first content
line. In `align`, `alignat`, and `flalign` variants, a label before a row
terminator moves to its own line immediately after that `\\`.

## Usage

```powershell
python -m latex_toolkit.eqnum_label .\paper.tex
python -m latex_toolkit.eqnum_label .\paper.tex -o .\paper.out.tex
python -m latex_toolkit.eqnum_label --clipboard
Get-Content .\paper.tex -Raw | python -m latex_toolkit.eqnum_label --stdin
```

## Python API

`transform_text(source)` returns the normalized fragment or document.
