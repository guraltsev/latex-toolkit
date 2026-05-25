# `texmacs_latex_to_latex`

`texmacs_latex_to_latex` is a clipboard-only pipeline that prepares
TeXmacs-generated LaTeX for ordinary LaTeX use. It runs the same five
normalization steps as `texmacs_latex_to_llm_latex` and then deletes
configured unary wrapper macros.

## Use Cases

- Clean up TeXmacs LaTeX copied to the clipboard before pasting it into a
  document.
- Remove TeXmacs wrapper macros such as `\hide-preamble{...}` after the usual
  TeXmacs-to-LaTeX normalization steps.

## Usage

```powershell
python -m latex_toolkit.commands.texmacs_latex_to_latex
python -m latex_toolkit.commands.texmacs_latex_to_latex --macros-file C:\path\macros.toml
```

The command is clipboard-only. It does not accept input paths, output paths,
backup options, or configuration files beyond the deleted macro list.

## Options

| Option | Meaning |
| --- | --- |
| `--macros-file` | Optional absolute TOML path whose command list replaces the deleted macro list passed to `delete_macros`. |

## Examples

Clipboard before:

```tex
\hide-preamble{\usepackage{foo}}
$$\alpha$$
\begin{proof*}{Claim}Done.\end{proof*}
```

Clipboard after:

```tex

\[\alpha\]
\begin{proof}[Claim]Done.\end{proof}
```

## Behavior Notes

- The pipeline step order is `dollar2bracket`, `ltae2aligned`,
  `tmscript2substack`, `proofstar2proof`, `uni2tex`, then `delete_macros`.
- The macro file must be an absolute path. Its top-level `commands` array
  replaces the default deleted macro list; `macros` is also accepted as an
  alias.
- The clipboard is updated after each successful changing step, so a later
  expected failure leaves the same partial result as running the individual
  clipboard commands in sequence.

## Python API

Use `latex_toolkit.commands.texmacs_latex_to_latex.main.transform_text(text,
commands=None)` to run the same ordered transforms without touching the
clipboard. Pass `commands` to replace the default deleted macro list.
