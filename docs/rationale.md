# Rationale

This repository is built around five constraints:

1. `lt-cli` must stay thin and only dispatch `lt-cli <command> [args...]`
2. each command owns its own CLI parsing and behavior
3. shared code must live under `src/lib/`
4. mutating commands must share one overwrite-and-backup policy
5. library transforms should exchange a stable TeX data structure rather than raw strings alone

## Why the write policy belongs in tests

The biggest behavior drift in command collections usually happens in their CLI
surface. Once one mutating command grows `--in-place`, another defaults to
stdout, and a third skips backups, users can no longer predict what a command
will do to a source tree.

This repository now makes one rule explicit:

- mutating commands overwrite the input file by default
- `-o/--output` redirects output somewhere else
- `-B/--no-backup` suppresses backup creation
- `--in-place` is not part of the contract

The test suite enforces that rule for every command unless the command opts out
with `OVERWRITES_SOURCE_TEX = False`.

## Why `TexFile` is the right core abstraction

A plain string is enough for text rewriting, but not enough for a toolkit that
needs to preserve source identity across multiple steps. The new `TexFile`
structure carries both:

- the TeX source text
- the originating filename, or `None` for generated buffers

That is the smallest useful abstraction for the next stage of the project,
where generated buffers will also need extent metadata from included files.

## Why `expand-includes` moved fully into the library

Flattening includes is a source transformation, not a CLI concern. The command
should only parse arguments, decide where to write, and apply backup policy.

The transformation now lives in `lib.latex.expand_includes()` and returns an
anonymous `TexFile`. That keeps the command thin and makes the transformation
reusable from tests or other commands.

## Why subfiles support had to be added in the expansion layer

Supporting `\subfile{...}` is not just a regex change. When the `subfiles`
package includes a child document from the main file, the child preamble up to
`\begin{document}` is ignored, and `\end{document}` plus everything after it is
ignored as well. Handling only the command name would flatten the wrong text.

That is why the implementation now distinguishes between ordinary include
commands and subfile-style inclusion, and normalizes the child content before
continuing recursive expansion.

## Why this is not a stopgap

The repository does not patch one command at a time. The changes are at the
stable architectural seams:

- one reusable backup helper in `src/lib/backup.py`
- one shared TeX data structure in `src/lib/core.py`
- one reusable include-expansion library in `src/lib/latex.py`
- one explicit module-level opt-out for read-only commands
- one thin dispatcher in `src/lt_cli.py`

That keeps command behavior predictable while leaving room for more TeX-aware
metadata later.
