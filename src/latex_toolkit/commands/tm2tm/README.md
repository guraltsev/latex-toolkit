# `tm2tm`

`tm2tm` is a clipboard-only TeXmacs markup normalization pipeline. It reads the
system clipboard, runs `tm_alignedt2ltae`, and replaces the clipboard with the
result.

## Use Cases

- Normalize copied TeXmacs snippets without writing a temporary file.
- Use the same pipeline shape as the larger TeXmacs-to-LaTeX clipboard
  workflows.

## Usage

```powershell
python -m latex_toolkit.commands.tm2tm
.\tm2tm.cmd
```

The command is clipboard-only. It does not accept input paths, output paths, or
backup options.

## Options

This command exposes no command-specific options.

## Examples

Clipboard before:

```text
<aligned|t|<tformat|<table|<row|<cell|>|<cell|x>>>>>
```

Clipboard after:

```text
<ltae|<tformat|<table|<row|<cell|x>>>>>
```

## Behavior Notes

- The pipeline step order is `tm_alignedt2ltae`.
- The clipboard is updated only when the step changes the text.
- Expected step failures are reported as command failures and leave the
  clipboard at the last successfully written state.
- The root `tm2tm.cmd` file is a Windows launcher for the Python command.

## Python API

Use `latex_toolkit.commands.tm2tm.main.transform_text(text)` to run the same
ordered transforms without reading or writing the system clipboard.

## Related Commands

- `tm_alignedt2ltae` owns the transform used by this pipeline.
