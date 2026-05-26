# `latex_format`

Run the toolkit's LaTeX formatting pipeline: `dollar2bracket`, `uni2tex`,
`brace_unary_macros`, `snapper_format`, then `latex_indent`.

## Usage

```powershell
python -m latex_toolkit.commands.latex_format
python -m latex_toolkit.commands.latex_format paper.tex
python -m latex_toolkit.commands.latex_format paper.tex -o formatted.tex
python -m latex_toolkit.commands.latex_format --max-width 80
```
