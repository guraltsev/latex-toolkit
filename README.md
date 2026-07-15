# Sentence-per-line LaTeX transformer

This command formats LaTeX prose so every sentence begins on its own physical
source line. It preserves comments, existing intra-sentence newlines, math,
verbatim-like content, structural blocks, the input newline convention, and
the exact trailing newline run.

Captions and footnotes are formatted recursively. Footnote invocations are
also placed on separate source-line blocks, with `%`-terminated newlines when
needed to avoid introducing a TeX space.

## Installation

Python 3.11 or newer is required. Install the project and its pinned Snapper
binary:

```powershell
python -m pip install --editable .
```

The `snapper-fmt==0.7.9` distribution installs an executable named `snapper`.
The transformer reports a clear runtime error if that executable is missing.

## Usage

Format a file to the default sibling path, `paper_sentences.tex`:

```powershell
python -m sentence_per_line_transformer .\paper.tex
```

Choose an output path or transform the clipboard explicitly:

```powershell
sentence-per-line .\paper.tex --output .\revised.tex
python -m sentence_per_line_transformer --clipboard
```

File mode preserves its input. Clipboard mode rejects file and output paths,
and it leaves an empty clipboard unchanged.

## Python API

```python
from sentence_per_line_transformer import transform_text

result = transform_text("First sentence. Second sentence.")
print(result)
```

Output:

```text
First sentence.
Second sentence.
```

`transform_text()` accepts complete documents and fragments. For complete
documents, only top-level `document` bodies are formatted; preambles remain
unchanged. `process_file(input_path, output_path)` provides the UTF-8 file
workflow.

## Development

Run the observable behavior suite with the real pylatexenc parser and pinned
Snapper formatter:

```powershell
python -m pip install --editable . pytest
python -m pytest
```

The implementation design is in
`src/sentence-per-line-transformer/DESIGN.md`. Repository authoring rules are
linked from `AGENTS.md`.
