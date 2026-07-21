# sentence_per_line_transformer

Format LaTeX prose so each sentence begins on its own physical line while
preserving protected source regions. The command requires `snapper-fmt`.

## Usage

```powershell
python -m latex_toolkit.sentence_per_line_transformer .\paper.tex
python -m latex_toolkit.sentence_per_line_transformer .\paper.tex -o .\paper.out.tex
python -m latex_toolkit.sentence_per_line_transformer --clipboard
```

Without an output path, file mode writes `paper_sentences.tex` beside the
source. Clipboard mode replaces nonempty clipboard text and cannot be combined
with a file or output path.

## Python API

`transform_text(source)` formats complete document bodies or fragments.

