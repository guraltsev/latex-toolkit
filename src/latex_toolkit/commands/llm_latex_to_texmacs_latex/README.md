# `llm_latex_to_texmacs_latex`

`llm_latex_to_texmacs_latex` is a clipboard-only pipeline that prepares
LLM-friendly LaTeX for import back into TeXmacs-flavored LaTeX. It reads the
system clipboard and replaces it with text transformed by three existing
commands.

## Use Cases

- Normalize LLM-edited LaTeX before pasting it back into TeXmacs.
- Apply unary macro bracing, TeXmacs vertical delimiter spelling, and
  TeXmacs-style proof titles in one clipboard workflow.

## Usage

```powershell
python -m latex_toolkit.commands.llm_latex_to_texmacs_latex
python -m latex_toolkit.commands.llm_latex_to_texmacs_latex --macros-file C:\path\macros.toml
.\llm_latex_to_texmacs_latex.cmd --macros-file C:\path\macros.toml
```

The command is clipboard-only. Its optional positional path is a compatibility
spelling for the macro configuration file, not an input document path.

## Options

| Option | Meaning |
| --- | --- |
| `macros_file` | Optional absolute TOML path, accepted for compatibility with older launchers. |
| `--macros-file` | Optional absolute TOML path whose command list is passed to `brace_unary_macros`. It cannot be combined with `macros_file`. |

## Examples

Clipboard before:

```tex
$\bar x + \left\| x\right\|$
\begin{proof}[Claim]Done.\end{proof}
```

Clipboard after:

```tex
$\bar{x} + \left \lVert x\right \rVert$
\begin{proof*}{Claim}Done.\end{proof*}
```

Minimal macro configuration:

```toml
commands = ['\FT', '\bar', '\tilde']
```

## Behavior Notes

- The pipeline step order is `brace_unary_macros`,
  `texmacs_vert_delimiters`, then `proof2proofstar`.
- The macro file must be an absolute path. Its top-level `commands` array
  replaces the default unary macro list for the bracing step; `macros` is also
  accepted as an alias.
- Macro configuration is loaded before the clipboard is read, so invalid TOML
  fails without changing clipboard contents.
- The clipboard is updated after each successful changing step, so a later
  expected failure leaves the same partial result as running the individual
  clipboard commands in sequence.
- The root `llm_latex_to_texmacs_latex.cmd` file is a Windows launcher for the
  Python command.

## Python API

Use `latex_toolkit.commands.llm_latex_to_texmacs_latex.main.transform_text(text,
macros_file=None)` to run the same ordered transforms without touching the
clipboard. The `macros_file` argument has the same absolute-path and TOML
requirements as the CLI.

## Related Commands

- `texmacs_latex_to_llm_latex` is the reverse workflow.
- The individual pipeline steps are `brace_unary_macros`,
  `texmacs_vert_delimiters`, and `proof2proofstar`.
