# LaTeX Toolkit

Preservation-focused command-line transformations for LaTeX source.

## Commands

- `math_dollar2latex`: convert `$...$` math to `\(...\)`.
- `math_latex2dollar`: reverse delimiter conversion.
- `syntax_regularizer`: regularize LaTeX source layout.
- `eqnum_label`: normalize display-math label placement with or without `\eqnum`.
- `sentence_per_line`: place each prose sentence on its own line.
- `full_normalize`: compose math-delimiter, syntax, macro-bracing, and sentence formatting.
- `template`: customize a syntax-tree transformation.
- `brace_args`: brace parsed macro arguments and math scripts.
- `greek_unicode2latex`: convert recognized Unicode math symbols to LaTeX macros.
- `greek_latex2unicode`: convert recognized LaTeX math macros to Unicode symbols.

Run `setup.cmd` to create `.venv` from the `python` on `PATH` and
install the package and its dependencies into it (with `uv` when available,
otherwise with `venv` and `pip`). Commands never install dependencies at
runtime. The `src\lt_*.cmd` and `src\mdt_*.cmd` wrappers run with
`.venv\Scripts\python.exe` when it exists. The `src\lt_*.py` and `src\mdt_*.py`
scripts run a command with whichever Python starts them, for example
`python src\lt_full_normalize.py main.tex`: the toolkit loads from `src`, so that
Python needs only the dependencies, not the toolkit installed, and paths stay
relative to the current folder. Inside the activated
environment, run a command with `python -m latex_toolkit.<command_name>` or
the matching underscore-named console command, such as `full_normalize`. Each command
package has a local README with its usage, behavior, and Python API.
