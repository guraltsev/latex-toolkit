# brace_args

Make implicit single-token arguments explicit without changing their contents.
The command uses the LaTeX parser to add braces around unbraced mandatory macro
arguments and ungrouped math-script operands: for example, `\mathcal A`
becomes `\mathcal{A}`, `\frac12` becomes `\frac{1}{2}`, and `x_1^2` becomes
`x_{1}^{2}`. It preserves arguments that are already grouped, plus optional and
star arguments. The project shorthand commands `\FT`, `\mb`, `\mbb`, `\mbf`,
`\mc`, `\mf`, and `\ms` are recognized as one-mandatory-argument macros.

In a complete document, only top-level `document` bodies are changed; the
preamble is retained verbatim. Input without a `document` environment is
treated as a LaTeX fragment.

## Use Cases

- Normalize implicit macro arguments and math scripts before downstream tooling.
- Keep complete-document preambles unchanged while formatting document bodies.

## Usage

```powershell
python -m latex_toolkit.brace_args .\paper.tex
python -m latex_toolkit.brace_args .\paper.tex -o .\paper.braced.tex
python -m latex_toolkit.brace_args --clipboard
Get-Content .\paper.tex -Raw | python -m latex_toolkit.brace_args --stdin
```

Complete documents retain their preambles. Standalone LaTeX fragments are
transformed in full. File mode writes `paper_braced.tex` by default.

## Python API

`transform_text(source)` returns braced LaTeX source.

## Options

| Option | Meaning |
| --- | --- |
| `input` | UTF-8 LaTeX file to transform in place. |
| `-o`, `--output`, `--output-file` | Write a separate result and preserve the input. |
| `--clipboard` | Transform nonempty clipboard text. |
| `--stdin` | Read all source from stdin and write only transformed source to stdout. |
| `-B`, `--no-backup` | Skip the timestamped backup when overwriting the input. |

## Examples

`\mathcal A + x_1` becomes `\mathcal{A} + x_{1}`; already grouped arguments,
optional arguments, and star arguments remain unchanged.

## Behavior Notes

Complete documents keep their preambles unchanged. Invalid input-mode
combinations are rejected before transformation.

## Related Commands

`syntax_regularizer` is a neighboring source-layout transform; `template`
provides a customizable parser-based transformation skeleton.
