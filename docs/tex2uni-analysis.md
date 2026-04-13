# tex2uni / uni2tex integration analysis

## Problem statement

The repository did not yet expose any command for the functionality in the
starter files. The user-provided files were standalone scripts that depended on
external infrastructure (`infra.cli`, `infra.latex_parser`, `infra.tool_io`, and
`TexDocument`) that does not exist in `latex-toolkit`.

That meant the issue was not one missing flag in an existing command. The actual
integration gap was that `latex-toolkit` had no symbol-conversion command at
all, and the starter implementation carried its own command orchestration that
conflicted with toolkit conventions.

## Evidence from the repository

`src/lt_cli.py` dispatches commands strictly from `src/commands/<command>/main.py`.
That is the only command registration mechanism in this repo.

Mutating commands in this repo follow one enforced policy:

- overwrite the input `.tex` file by default
- support `-o/--output`
- support `-B/--no-backup`
- use `lib.backup.backup_file`
- avoid `--in-place`

That policy is enforced structurally by `tests/test_write_policy.py`.

Before this change, the available command set in `src/commands/` only contained:

- `expand-includes`
- `list-graphics`
- `strip-comments`

So the missing functionality symptom was real and repo-level: there was nowhere
for `lt-cli tex2uni ...` or `lt-cli uni2tex ...` to dispatch.

## Evidence from the starter files

The starter files already showed that the conversion itself was one shared
feature split across two scripts:

- both scripts split the document around `\begin{document}` / `\end{document}`
- both iterate mutable math-mode regions only
- both preserve comments and text-mode content
- both perform the same file-loading / writing / parser orchestration
- the only material difference is direction-specific token replacement

That means the core source problem was duplicated orchestration around one
transformation, not two truly separate tools.

## Core source of the problem

The core source was an architectural mismatch between the starter code and the
repository:

1. the repository expects shared transformation logic under `src/lib/`
2. the repository expects thin command wrappers under `src/commands/`
3. the starter files bundled transform logic and standalone CLI plumbing into two
   separate scripts

If this had been solved by copying both scripts into the repo with minimal edits,
that would have preserved the duplication and still left the real source of the
problem in place.

## Implemented solution

The implemented fix moves the shared conversion logic into new library modules:

- `src/lib/symbol_mappings.py`
- `src/lib/math_unicode.py`

Then it exposes the functionality through actual toolkit commands:

- `src/commands/tex2uni/main.py`
- `src/commands/uni2tex/main.py`

### Why this is the correct approach

This matches the repo's actual architecture:

- `lt-cli` can now discover the commands naturally through `src/commands/`
- conversion logic is reusable and lives under `src/lib/`
- both mutating commands follow the repo's overwrite-and-backup policy
- `uni2tex` reuses the same command implementation path as reverse-mode
  `tex2uni`, so the two directions stay synchronized

### Why this is not a stopgap

This does not patch symptoms such as command naming alone.

It removes the duplicated orchestration from the starter design and places the
shared functionality at the repository's stable seams:

- one canonical mapping table
- one conversion engine
- one primary command with a reverse mode
- one alias command for the reverse direction
- one fixture-based command test suite integrated into the repo

### Why this is scoped correctly

The change only touches the parts relevant to the missing feature:

- new library code for symbol conversion
- new command entries for dispatch
- documentation for the new commands
- tests for command behavior and CLI visibility

Existing unrelated commands and unrelated library helpers were left unchanged.
