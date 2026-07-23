# greek_unicode2latex

Convert Unicode Greek symbols to conventional LaTeX macros only in parsed math
mode. Inline/display delimiters and common math environments are supported;
prose, comments, and complete-document preambles are preserved.

```powershell
python -m latex_toolkit.greek_unicode2latex .\paper.tex
python -m latex_toolkit.greek_unicode2latex --clipboard
Get-Content .\paper.tex -Raw | python -m latex_toolkit.greek_unicode2latex --stdin
```

`transform_text(source)` returns the converted source.
