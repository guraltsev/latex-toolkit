# brace_args

Make implicit single-token arguments explicit without changing their contents.
The command uses the LaTeX parser to add braces around unbraced mandatory macro
arguments and ungrouped math-script operands: for example, `\mathcal A`
becomes `\mathcal{A}`, `\frac12` becomes `\frac{1}{2}`, and `x_1^2` becomes
`x_{1}^{2}`. It preserves arguments that are already grouped, plus optional and
star arguments. The project shorthand commands `\FT`, `\mb`, `\mbb`, `\mbf`,
`\mc`, `\mf`, and `\ms` are recognized as one-mandatory-argument macros.

In a complete document, only top-level `document` bodies are changed; the
preamble is retained verbatim. Input without a `document` environment is
treated as a LaTeX fragment.

## Usage

```powershell
python -m latex_toolkit.brace_args .\paper.tex
python -m latex_toolkit.brace_args .\paper.tex -o .\paper.braced.tex
python -m latex_toolkit.brace_args --clipboard
Get-Content .\paper.tex -Raw | python -m latex_toolkit.brace_args --stdin
```

Complete documents retain their preambles. Standalone LaTeX fragments are
transformed in full. File mode writes `paper_braced.tex` by default.

## Python API

`transform_text(source)` returns braced LaTeX source.
