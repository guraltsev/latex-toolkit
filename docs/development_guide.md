# Development Guide

This guide records project-level architecture rules that are broader than
ordinary Python style, docstring format, or test policy.

## Library Boundary

`src/latex_toolkit/lib/` is for meaningful shared code.

Put code in `lib` only when it is reusable across command families, represents
shared infrastructure, or is an intentional public Python building block. Good
examples include file backup policy, clipboard boundaries, TeX file I/O, and
LaTeX parsing primitives used by multiple unrelated commands.

Do not move command-specific behavior into `lib` merely to avoid import
awkwardness, to make tests easier to write, or to make a command file shorter.
If behavior belongs to one command family, keep it with that command family.

The current intentional shared library modules are:

- `backup`: file backup policy shared by mutating commands.
- `clipboard`: the system clipboard boundary used by clipboard-enabled
  commands.
- `core`: the `TexFile` value object and TeX file I/O helpers.
- `latex`: lightweight LaTeX source inspection, comment handling, include
  traversal, and small public text helpers shared by multiple commands.
- `latex_parser`: tokenization and document-region primitives used by command
  transforms.
- `logging_config`: command execution wrappers and logging setup.

Command-family transforms live under `src/latex_toolkit/commands/` with the
command packages that own them. Public command-level text transforms are
exposed through each command package's `main.transform_text(...)` when a direct
Python entrypoint is useful.

## Command Package Names

Command package directories use underscores, not dashes.

Use valid Python identifiers for command module names so commands can import
each other directly and normal Python tooling can inspect them without special
loading code. User-facing documentation may describe historical or shell-facing
spellings, but source package directories should keep underscore names.

## Direct And Reverse Commands

Direct and reverse commands are allowed and encouraged to import from each
other when they are one command family.

For example, a reverse command may call the direct command's parser,
`transform_text`, or `main` with a forced reverse option. Prefer this over
moving command-family implementation code into `lib`. Shared command-family
code should live near the commands that own it unless it becomes meaningful
shared infrastructure for unrelated command families.

## Command Write Behavior

File-transforming commands share an observable write contract. By default, a
command called with an input path overwrites that input after saving its
original contents in a timestamped backup under `.backup`. The `-B` and
`--no-backup` options skip backup creation. The `-o`, `--output`, and
`--output-file` options write the transformed text to a separate path, preserve
the source file, and do not create a backup.

Clipboard mode is also part of the user-facing command contract. Commands with
`--clipboard` read text from the system clipboard, write transformed text back
to the system clipboard, and reject simultaneous input or output paths with a
parser error.

Permanent tests should protect those user-visible effects by invoking the CLI
or a public command entrypoint and mocking only real boundaries such as the
system clipboard. Do not add permanent tests for helper imports, package
metadata, marker constants, dispatcher absence, or other implementation choices.
Use this guide and local source comments for architecture constraints that are
important but not directly observable.
