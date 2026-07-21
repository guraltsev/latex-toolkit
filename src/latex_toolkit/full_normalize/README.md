# full_normalize

Apply syntax regularization, sentence-per-line formatting, and a final syntax
regularization pass as one command-family pipeline.

## Usage

```powershell
python -m latex_toolkit.full_normalize .\paper.tex
python -m latex_toolkit.full_normalize .\paper.tex -o .\paper.out.tex
python -m latex_toolkit.full_normalize --clipboard
```

Without an output path, file mode writes `paper_full_normalized.tex` beside the
source. Clipboard mode replaces nonempty clipboard text and cannot be combined
with a file or output path.

## Python API

`transform_text(source)` runs the complete pipeline in memory.

