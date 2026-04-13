# latex-toolkit

`latex-toolkit` is a small Python toolkit for command-line work on LaTeX sources.
It is built around a thin dispatcher, small focused commands, and a shared library
layer for reusable TeX transforms.

## Install

From the repository root:

```bash
pip install .
```

That exposes:

```bash
lt-cli
```

## Quick start

```bash
lt-cli strip-comments paper.tex
lt-cli strip-comments paper.tex -o paper.clean.tex
lt-cli expand-includes thesis.tex
lt-cli expand-includes thesis.tex -o thesis.flat.tex
lt-cli list-graphics thesis.tex --unique
```

## What the commands do

### `strip-comments`

Removes LaTeX `%` comments while preserving escaped percent signs such as `\%`.

### `expand-includes`

Flattens a document by recursively expanding `\input{...}`, `\include{...}`,
`\subfile{...}`, and `\subfileinclude{...}` references.

### `list-graphics`

Lists `\includegraphics{...}` targets, optionally across recursively included
source files.

## Commands that rewrite `.tex` files

This repository has one explicit policy for commands that overwrite a source
`.tex` file.

Those commands must:

- import `backup_file` from `lib.backup`
- expose `-B` / `--no-backup`
- overwrite the input file by default
- use `-o` / `--output` to redirect output somewhere else
- avoid a `--in-place` flag entirely

In other words, overwriting is the default write mode for mutating commands.
When callers want a different destination, they pass `-o`.

Here is a snippet on how to do this
``` python
import argparse
# ...
from lib.backup import backup_file
from pathlib import Path
# ...

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
	# ...
    )
    parser.add_argument("input",
	# ...
	)
    parser.add_argument(
        "-o",
        "--output",
        help="Write expanded output to this path instead of overwriting the input file.",
    )
    parser.add_argument(
        "-B",
        "--no-backup",
        action="store_true",
        help="Do not create a backup before overwriting the input file.",
    )
    parser.add_argument(
        "--backup-dir",
        default=".lt-backup",
        help="Relative or absolute directory for backups when overwriting. Default: %(default)s",
    )
    return parser
	
# ...
def main(argv: list[str] | None = None) -> int:
# ...
	parser = build_parser()
    args = parser.parse_args(argv)
# ...
    input_path = Path(args.input).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve() if args.output else input_path

    if output_path == input_path and not args.no_backup:
        backup_file(input_path, args.backup_dir)
# ...
```

This behavior is tested by the test suite. To opt out and declare that you do not modify the input tex file define globally in your module/command
``` python
OVERWRITES_SOURCE_TEX = False
```

## Backup behavior

Shared backup behavior lives in `src/lib/backup.py`.

Default behavior:

- backups go in `.lt-backup`
- relative backup directories are resolved against the input file's parent directory
- backup timestamps are in UTC
- filenames follow `filename.ext.backup.YYYYMMDD:HHMMSS`
- collisions in the same second receive a numeric suffix such as `.01`

## Library core

The shared library includes a core `TexFile` data structure in
`src/lib/core.py`.

It stores:

- the LaTeX source string
- the source filename as a `Path`, or `None` for generated buffers

That gives library functions a stable return type today and leaves room for
future metadata such as source extents from expanded includes.

## Common command behavior

`lt-cli` dispatches in this shape:

```bash
lt-cli <command> [command arguments...]
```

Each command owns its own argument parsing and behavior.

Examples:

```bash
lt-cli expand-includes thesis.tex
lt-cli expand-includes thesis.tex -o flat.tex
lt-cli strip-comments draft.tex
lt-cli list-graphics thesis.tex --with-source
```

## Project layout

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
│       ├── core.py
│       └── latex.py
└── tests/
    ├── test_backup.py
    ├── test_commands.py
    ├── test_latex.py
    ├── test_lt_cli.py
    └── test_write_policy.py
```

## Technical details

### Thin dispatcher

`src/lt_cli.py` stays intentionally small. It resolves
`src/commands/<command>/main.py`, loads it, and forwards the remaining argv
unchanged.

### Relocatable imports

Commands import shared helpers through `lib.*`, for example:

```python
from lib.backup import backup_file
from lib.latex import expand_includes
```

This keeps command code stable in two modes:

1. **Toolkit mode**: `src/` is the import root, so `src/lib/` is importable as `lib`.
2. **Standalone mode**: a command folder can be copied out together with a sibling `lib/` directory and keep the same imports.

Example standalone extraction:

```text
src/commands/expand-includes/   ->   /expand-includes/
src/lib/backup.py               ->   /expand-includes/lib/backup.py
src/lib/core.py                 ->   /expand-includes/lib/core.py
src/lib/latex.py                ->   /expand-includes/lib/latex.py
```

### Scope notes

These commands are intentionally small and predictable. They handle common
LaTeX source patterns well, but they are not full TeX parsers. For example,
they do not attempt to interpret arbitrary macro-generated filenames or every
package-specific include primitive.
