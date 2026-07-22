# LaTeX Toolkit

Preservation-focused command-line transformations for LaTeX source.

## Commands

- `dollar_math_to_latex_delimiters`: convert `$...$` math to `\(...\)`.
- `latex_delimiters_to_dollar_math`: reverse delimiter conversion.
- `syntax_regularizer`: regularize LaTeX source layout.
- `sentence_per_line_transformer`: place each prose sentence on its own line.
- `full_normalize`: compose syntax and sentence formatting.
- `latex_transformer_template`: customize a syntax-tree transformation.
- `latex_argument_bracer`: brace parsed macro arguments and math scripts.

Install the package with `python -m pip install --editable .`, then run a
command with `python -m latex_toolkit.<command_name>`. Each command package
has a local README with its usage, behavior, and Python API.
