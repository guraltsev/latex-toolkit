# `texmacs_latex_to_llm_latex`

`texmacs_latex_to_llm_latex` is a clipboard-only pipeline that prepares
TeXmacs-generated LaTeX for LLM editing. It reads the system clipboard and
replaces it with text transformed by five existing commands.

## Use Cases

- Clean up LaTeX copied from TeXmacs before pasting it into an LLM.
- Convert TeXmacs-specific proof, script, delimiter, and symbol forms into the
  toolkit's LLM-friendly conventions.

## Usage

```powershell
python -m latex_toolkit.commands.texmacs_latex_to_llm_latex
.\texmacs_latex_to_llm_latex.cmd
```

The command is clipboard-only. It does not accept input paths, output paths,
backup options, or configuration files.

## Options

This command exposes no command-specific options.

## Examples

Clipboard before:

```tex
$$\alpha$$
\begin{ltae}x\\y\end{ltae}
\begin{proof*}{Claim}Done.\end{proof*}
```

Clipboard after:

```tex
\[\alpha\]
\begin{aligned}[t]&x\\&y\end{aligned}
\begin{proof}[Claim]Done.\end{proof}
```

## Behavior Notes

- The pipeline step order is `dollar2bracket`, `ltae2aligned`,
  `tmscript2substack`, `proofstar2proof`, then `uni2tex`.
- Each step receives the previous step's output.
- The clipboard is updated after each successful changing step, so a later
  expected failure leaves the same partial result as running the individual
  clipboard commands in sequence.
- The root `texmacs_latex_to_llm_latex.cmd` file is a Windows launcher for the
  Python command.

## Python API

Use `latex_toolkit.commands.texmacs_latex_to_llm_latex.main.transform_text(text)`
to run the same ordered transforms without reading or writing the system
clipboard.

## Related Commands

- `llm_latex_to_texmacs_latex` is the reverse workflow.
- The individual pipeline steps are `dollar2bracket`, `ltae2aligned`,
  `tmscript2substack`, `proofstar2proof`, and `uni2tex`.
