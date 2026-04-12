# latex-toolkit

`latex-toolkit` is a small Python toolkit for command-line work on LaTeX sources.

It is organized so that:

- all shared source lives under `src/`
- the top-level CLI entrypoint is `src/lt_cli.py`
- reusable helpers live under `src/lib/`
- each command lives in its own directory under `src/commands/<command-name>/`
- command code can keep importing `lib.*` whether it is used inside the toolkit or extracted into a standalone command folder with a sibling `lib/`

## Layout

```text
latex-toolkit/
├── pyproject.toml
├── README.md
├── docs/
│   └── rationale.md
├── src/
│   ├── lt_cli.py
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── expand-includes/
│   │   │   ├── README.md
│   │   │   └── main.py
│   │   ├── list-graphics/
│   │   │   ├── README.md
│   │   │   └── main.py
│   │   └── strip-comments/
│   │       ├── README.md
│   │       └── main.py
│   └── lib/
│       ├── __init__.py
│       ├── backup.py
│       └── latex.py
└── tests/
    ├── test_backup.py
    ├── test_commands.py
    └── test_lt_cli.py
```

## Installation

From the repository root:

```bash
pip install .
```

That exposes:

```bash
lt-cli
```

## Dispatcher behavior

`lt-cli` is intentionally thin. It only parses invocations in this shape:

```bash
lt-cli <command> [command arguments...]
```

The dispatcher resolves `src/commands/<command>/main.py`, loads it, and forwards the remaining arguments unchanged. Each command is responsible for its own CLI processing.

Examples:

```bash
lt-cli expand-includes thesis.tex -o flat.tex
lt-cli strip-comments draft.tex --in-place
lt-cli list-graphics thesis.tex --unique
```

## Relocatable command imports

Commands import shared helpers through `lib.*`, for example:

```python
from lib.backup import backup_file
from lib.latex import expand_includes
```

This works in both modes:

1. **Toolkit mode**: `src/` is the import root, so `src/lib/` is importable as `lib`.
2. **Standalone mode**: if a command directory is copied out as its own root and the needed libraries are copied into `<command-root>/lib/`, the imports stay exactly the same.

Example standalone extraction:

```text
src/commands/expand-includes/   ->   /expand-includes/
src/lib/backup.py               ->   /expand-includes/lib/backup.py
src/lib/latex.py                ->   /expand-includes/lib/latex.py
```

The Python inside `expand-includes/` stays unchanged because it still imports from `lib.*`.

## Backup convention

Shared backup behavior lives in `src/lib/backup.py`.

Use:

```python
from lib.backup import backup_file
```

Behavior:

- default backup directory: `.lt-backup`
- relative backup directories are resolved against the input file's parent directory
- backups are timestamped in UTC
- default backup filename pattern:

```text
filename.ext.backup.YYYYMMDD:HHMMSS
```

If multiple backups are created in the same second, a numeric suffix is appended:

```text
filename.ext.backup.YYYYMMDD:HHMMSS.01
```

## Command policy

All commands that overwrite or mutate input files should:

- import `backup_file` from `lib.backup`
- create a backup before the write
- expose `--no-backup` and `-B`
- optionally expose `--backup-dir` when callers need a different relative backup folder

Read-only commands do not need backup handling.

## Included commands

### `expand-includes`

Recursively expands `\\input{...}` and `\\include{...}` references into a single flattened document.

### `strip-comments`

Removes LaTeX `%` comments while preserving escaped percent signs such as `\\%`.

### `list-graphics`

Lists `\\includegraphics{...}` targets, optionally across recursively included files.

## Scope notes

These commands are intentionally small and predictable. They handle common LaTeX source patterns well, but they are not full TeX parsers. For example, they do not attempt to interpret arbitrary macro-generated filenames or every package-specific include primitive.
