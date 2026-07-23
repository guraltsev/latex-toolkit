# Command Documentation Guide

Each public command package under `src/` must have  a local
`README.md` that explains:
- what the command does
- how to run the command

The root `README.md` is a short summary of the toolkit with links to per-command `README.md`

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

Mention public callable entrypoints when useful, usually the command module's
`transform_text(...)`. For pipeline commands, mention whether the Python
API accepts configuration such as `macros_file`.

Reverse-alias commands explicitly say which command they call and which
direction is forced. For example, `proof2proofstar` is the reverse-direction
alias for `proofstar2proof`; it does not expose an independent `--reverse`
flag.

## Related Commands

List reverse commands, pipeline neighbors, or command-family siblings.

Commands with configuration files include the minimal valid file shape, path
requirements, replacement-vs-extension semantics, and failure behavior before
input or clipboard contents are changed.

## Naming

Use the importable package directory as the canonical README title and Python
module path, for example `strip_comments`.
