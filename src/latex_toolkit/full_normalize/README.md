# full_normalize

Apply the toolkit's complete layout-normalization pipeline: syntax
regularization, prose sentence-per-line formatting, then syntax regularization
again. The first and last stages remove ordinary indentation, unwrap eligible
inline math, and normalize structural line breaks; the middle stage joins
wrapped prose and starts each sentence on its own line. The final pass ensures
the sentence formatter's output follows the same syntax-layout rules.

The pipeline preserves protected math, table-like, verbatim-like, and
structural source regions according to its component commands. In complete
documents it changes only top-level `document` bodies; fragments are processed
in full. It requires `snapper-fmt` through the sentence-formatting stage.

## Usage

```powershell
python -m latex_toolkit.full_normalize .\paper.tex
python -m latex_toolkit.full_normalize .\paper.tex -o .\paper.out.tex
python -m latex_toolkit.full_normalize --clipboard
Get-Content .\paper.tex -Raw | python -m latex_toolkit.full_normalize --stdin
```

Without an output path, file mode writes `paper_full_normalized.tex` beside the
source. Clipboard mode replaces nonempty clipboard text. Standard-stream mode
reads stdin and writes only the transformed text to stdout. Neither mode can be
combined with a file or output path.

## Python API

`transform_text(source)` runs the complete pipeline in memory.
