# latex_argument_bracer

Brace parsed mandatory LaTeX macro arguments and math subscripts and
superscripts. It turns `\mathcal A` into `\mathcal{A}`, `\frac12` into
`\frac{1}{2}`, and `x_1` into `x_{1}`. The project shorthand commands `\FT`,
`\mb`, `\mbb`, `\mbf`, `\mc`, `\mf`, and `\ms` are supported as
one-argument commands.

## Usage

```powershell
python -m latex_toolkit.latex_argument_bracer .\paper.tex
python -m latex_toolkit.latex_argument_bracer .\paper.tex -o .\paper.braced.tex
python -m latex_toolkit.latex_argument_bracer --clipboard
Get-Content .\paper.tex -Raw | python -m latex_toolkit.latex_argument_bracer --stdin
```

Complete documents retain their preambles. Standalone LaTeX fragments are
transformed in full. File mode writes `paper_braced.tex` by default.

## Python API

`transform_text(source)` returns braced LaTeX source.
