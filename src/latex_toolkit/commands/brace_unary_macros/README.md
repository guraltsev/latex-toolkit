# `brace_unary_macros`

Adds braces around the next unbraced token passed to configured unary macros:

```powershell
python -m latex_toolkit.commands.brace_unary_macros .\paper.tex
```

The default command list includes `\FT`, `\bar`, `\tilde`, `\dot`, and common
math accent variants. Replace the list with an absolute TOML path:

```toml
commands = ['\FT', '\bar', '\tilde']
```

```powershell
python -m latex_toolkit.commands.brace_unary_macros .\paper.tex --macros-file C:\path\macros.toml
```
