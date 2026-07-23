# LaTeX Toolkit

Preservation-focused command-line transformations for LaTeX source.

## Commands

- `math_dollar2latex`: convert `$...$` math to `\(...\)`.
- `math_latex2dollar`: reverse delimiter conversion.
- `syntax_regularizer`: regularize LaTeX source layout.
- `sentence_per_line`: place each prose sentence on its own line.
- `full_normalize`: compose syntax and sentence formatting.
- `template`: customize a syntax-tree transformation.
- `brace_args`: brace parsed macro arguments and math scripts.

Install the package with `python -m pip install --editable .`, then run a
command with `python -m latex_toolkit.<command_name>`. Each command package
has a local README with its usage, behavior, and Python API.
