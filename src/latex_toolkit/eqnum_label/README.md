# eqnum_label

Normalize adjacent `\eqnum\label{...}` pairs in display math. The command
always writes one space between the macros. In `\[...\]`, `equation`, and
`equation*` displays, a single pair that occupies its own source line is moved
to the first content line. Pairs in multi-row environments remain in place,
because their position can select a particular equation row.

## Usage

```powershell
python -m latex_toolkit.eqnum_label .\paper.tex
python -m latex_toolkit.eqnum_label .\paper.tex -o .\paper.out.tex
python -m latex_toolkit.eqnum_label --clipboard
Get-Content .\paper.tex -Raw | python -m latex_toolkit.eqnum_label --stdin
```

## Python API

`transform_text(source)` returns the normalized fragment or document.
