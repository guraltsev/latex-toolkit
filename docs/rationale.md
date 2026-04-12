# Rationale

This repository is built around four constraints:

1. `lt-cli` must stay thin and only dispatch `lt-cli <command> [args...]`.
2. each command owns its own CLI parsing and behavior
3. shared code must live under `src/lib/`
4. command code should keep the same `from lib...` imports when extracted into a standalone command directory with a sibling `lib/`

## Why this is the right structure

A thin dispatcher avoids duplicating option parsing rules in two places. The root
CLI should not need to understand command-specific flags, because every command
is explicitly responsible for its own CLI processing.

Using `src/lib/` as the only shared import root also solves the portability
requirement. Command code imports from `lib.*` in both modes:

- inside the toolkit, because `src/` is the import root
- outside the toolkit, because the extracted command directory can carry its own `lib/`

That keeps command code unchanged when moved.

## Why the backup helper had to change

The supplied helper was a useful starting point because it already centralized
backup creation and collision handling. But the requested contract is different:

- backups must live in `.lt-backup` by default
- timestamps must be UTC
- the filename pattern must be `filename.ext.backup.YYYYMMDD:HHMMSS`
- commands should import the helper directly instead of assuming a different
  repository-specific write funnel

The new `src/lib/backup.py` implements exactly that contract and nothing more.
It does not absorb unrelated CLI logic, so it stays reusable from every mutating
command.

## Why the solution is not a stopgap

This repository does not patch around symptoms such as backup naming in a single
command. Instead, it changes the architecture at the correct seam:

- one reusable backup library in `src/lib/backup.py`
- one dispatcher in `src/lt_cli.py`
- one directory per command in `src/commands/`
- one import convention (`from lib...`) that works in both toolkit and extracted modes

That is the stable boundary the project needs if more LaTeX commands are added
later.
