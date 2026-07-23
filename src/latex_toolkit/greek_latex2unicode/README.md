# greek_latex2unicode

Convert conventional LaTeX Greek macros to Unicode symbols only in parsed math
mode. This is the reverse of `greek_unicode2latex` and preserves prose,
comments, and complete-document preambles.

```powershell
python -m latex_toolkit.greek_latex2unicode .\paper.tex
python -m latex_toolkit.greek_latex2unicode --clipboard
Get-Content .\paper.tex -Raw | python -m latex_toolkit.greek_latex2unicode --stdin
```

`transform_text(source)` returns the converted source.
