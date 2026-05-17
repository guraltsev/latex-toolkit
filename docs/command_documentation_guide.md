# Command Documentation Guide

Each public command package under `src/latex_toolkit/commands/` owns a local
`README.md`. The local README is the user-facing contract for that command:
it should explain how to run the command and what observable behavior remains
stable without requiring users to inspect Python docstrings or source files.

Keep the root `README.md` as a short command index. Put command-specific
options, examples, side effects, and limitations in the command package
README.

## README Shape

Use this structure unless a command has a strong reason to differ:

````markdown
# `<package_name>`

One short paragraph stating the command purpose, source syntax, and target
syntax. Mention the historical help label if it differs from the package name.

## Use Cases

- Common case where this command is the right tool.
- Any important reverse or pipeline relationship.

## Usage

```powershell
python -m latex_toolkit.commands.<package_name> .\paper.tex
python -m latex_toolkit.commands.<package_name> .\paper.tex -o .\paper.out.tex
python -m latex_toolkit.commands.<package_name> --clipboard
```

State whether the command supports file mode, clipboard mode, both, or only a
pipeline clipboard mode.

## Options

| Option | Meaning |
| --- | --- |
| `input` | Input path semantics, if supported. |
| `-o`, `--output`, `--output-file` | Output path behavior, if supported. |
| `--clipboard` | Clipboard behavior, if supported. |
| `-B`, `--no-backup` | Backup behavior, if supported. |
| command-specific option | Command-specific contract. |

Omit options the command does not expose.

## Examples

Show small before-and-after examples for mutating transforms, stdout examples
for reporting commands, and input/output clipboard examples for clipboard-only
pipelines.

## Behavior Notes

- What is deliberately converted.
- What is deliberately preserved.
- How comments, escaped syntax, nested environments, include paths, duplicate
  results, unmatched delimiters, or invalid options behave.
- Any external tool or configuration file requirements.

## Python API

Mention public callable entrypoints when useful, usually
`main.transform_text(...)`. For pipeline commands, mention whether the Python
API accepts configuration such as `macros_file`.

## Related Commands

List reverse commands, pipeline neighbors, or command-family siblings.
````

## Command Types

File-transforming commands document the shared write contract from
`docs/development_guide.md`: calling the command with an input path overwrites
that input after saving a timestamped backup under `.backup`; `-B` or
`--no-backup` skips that backup; `-o`, `--output`, or `--output-file` writes a
separate output path, leaves the source file unchanged, and does not create a
backup. `--backup-dir` changes the backup directory only for overwriting file
mode. `--clipboard` reads the system clipboard, replaces it with transformed
text, and rejects simultaneous input or output paths.

Read-only reporting commands say that they print to standard output and do
not rewrite source files. If clipboard mode is supported, document that the
clipboard is replaced with the rendered report.

Clipboard-only pipeline commands make that constraint obvious near the top.
They list each pipeline step in order, explain why the pipeline is useful as a
workflow, and document configuration passed into any inner step. A pipeline
updates the clipboard after each successful changing step, so a later expected
failure leaves the same partial clipboard result as running the individual
commands in sequence.

Reverse-alias commands explicitly say which command they call and which
direction is forced. For example, `proof2proofstar` is the reverse-direction
alias for `proofstar2proof`; it does not expose an independent `--reverse`
flag.

Commands with configuration files include the minimal valid file shape, path
requirements, replacement-vs-extension semantics, and failure behavior before
input or clipboard contents are changed.

## Naming

Use the importable package directory as the canonical README title and Python
module path, for example `strip_comments`. Mention historical dash spellings,
such as `strip-comments`, only as help/log labels or intentionally supported
wrappers.
