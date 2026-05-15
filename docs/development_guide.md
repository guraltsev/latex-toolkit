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
