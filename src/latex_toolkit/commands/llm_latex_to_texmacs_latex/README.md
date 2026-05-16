# `llm_latex_to_texmacs_latex`

Runs the clipboard pipeline for LLM-friendly LaTeX headed back to TeXmacs.

```powershell
python -m latex_toolkit.commands.llm_latex_to_texmacs_latex
python -m latex_toolkit.commands.llm_latex_to_texmacs_latex --macros-file C:\path\macros.toml
.\llm_latex_to_texmacs_latex.cmd --macros-file C:\path\macros.toml
```

The pipeline runs `brace_unary_macros`, `texmacs_vert_delimiters`, and
`proof2proofstar` in that order. The `--macros-file` option is passed to the
unary macro bracing step.
