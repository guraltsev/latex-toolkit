# `texmacs_latex_to_llm_latex`

Runs the clipboard pipeline for TeXmacs-generated LaTeX before sending text to
an LLM.

```powershell
python -m latex_toolkit.commands.texmacs_latex_to_llm_latex
.\texmacs_latex_to_llm_latex.cmd
```

The pipeline runs `dollar2bracket`, `ltae2aligned`, `tmscript2substack`,
`proofstar2proof`, and `uni2tex` in that order.
