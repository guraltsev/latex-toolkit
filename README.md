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
lt-cli tex2uni paper.tex
lt-cli tex2uni paper.tex --reverse
lt-cli uni2tex paper.tex
lt-cli aligned2baea paper.tex
lt-cli aligned2baea paper.tex --reverse
lt-cli baea2aligned paper.tex
lt-cli eqn-star2dmath paper.tex
lt-cli eqn-star2dmath paper.tex --reverse
lt-cli dmath2eqn-star paper.tex
lt-cli eqn2dmath-eqnum paper.tex
lt-cli eqn2dmath-eqnum paper.tex --reverse
lt-cli dmath-eqnum2eqn paper.tex
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

### `tex2uni`

Converts a mapped set of LaTeX math macros to Unicode symbols, limited to
mutable math-mode content. The same command also supports the reverse direction
through `--reverse`.

### `uni2tex`

Runs the reverse-direction conversion from mapped Unicode math symbols back to
LaTeX macros.

### `aligned2baea`

Compresses exact `\begin{aligned}[t] ... \end{aligned}` blocks into the local
`\ba ... \ea` shorthand. With `--reverse`, it expands the shorthand back to
explicit `aligned` environments.

### `baea2aligned`

Runs the reverse-direction conversion from `\ba` / `\ea` back to explicit
`aligned` environments.

### `eqn-star2dmath`

Rewrites `equation*` environments as plain `\[ ... \]` display math. The same
command also supports the reverse direction through `--reverse`, which rewrites
plain display math back to `equation*` while leaving standalone `\eqnum`
blocks untouched.

### `dmath2eqn-star`

Runs the reverse-direction conversion from plain `\[ ... \]` display math back
to `equation*` environments.

### `eqn2dmath-eqnum`

Rewrites `equation` environments as `\[\eqnum ... \]` numbered-display blocks.
The same command also supports the reverse direction through `--reverse`, which
rewrites only standalone `\eqnum`-prefixed display math back to `equation`.

### `dmath-eqnum2eqn`

Runs the reverse-direction conversion from `\[\eqnum ... \]` display math back
to `equation` environments.

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

### How the test suite enforces this

The test suite treats every command as a source-overwriting command unless the
command module explicitly opts out with:

```python
OVERWRITES_SOURCE_TEX = False
```

That declaration is for read-only commands such as `list-graphics`.
Any command that does not opt out is expected to follow the write-policy rules
above.

## Backup behavior

Shared backup behavior lives in `src/lib/backup.py`.

Default behavior:

- backups go in `.lt-backup`
- relative backup directories are resolved against the input file's parent directory
- backup timestamps are in UTC
- filenames follow `filename.ext.backup.YYYYMMDD:HHMMSS`
- collisions in the same second receive a numeric suffix such as `.01`

## Library core

The shared library now includes a core `TexFile` data structure in
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
lt-cli tex2uni draft.tex
lt-cli uni2tex draft.tex
lt-cli eqn-star2dmath draft.tex
lt-cli dmath2eqn-star draft.tex
lt-cli eqn2dmath-eqnum draft.tex
lt-cli dmath-eqnum2eqn draft.tex
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
│   │   ├── strip-comments/
│   │   │   ├── README.md
│   │   │   └── main.py
│   │   ├── tex2uni/
│   │   │   ├── README.md
│   │   │   └── main.py
│   │   ├── uni2tex/
│   │   │   ├── README.md
│   │   │   └── main.py
│   │   ├── aligned2baea/
│   │   │   ├── README.md
│   │   │   └── main.py
│   │   ├── baea2aligned/
│   │   │   ├── README.md
│   │   │   └── main.py
│   │   ├── eqn-star2dmath/
│   │   │   ├── README.md
│   │   │   └── main.py
│   │   ├── dmath2eqn-star/
│   │   │   ├── README.md
│   │   │   └── main.py
│   │   ├── eqn2dmath-eqnum/
│   │   │   ├── README.md
│   │   │   └── main.py
│   │   └── dmath-eqnum2eqn/
│   │       ├── README.md
│   │       └── main.py
│   └── lib/
│       ├── __init__.py
│       ├── aligned_baea.py
│       ├── backup.py
│       ├── core.py
│       ├── equation_eqnum_displaymath.py
│       ├── equation_star_displaymath.py
│       ├── latex.py
│       ├── latex_parser.py
│       ├── math_unicode.py
│       └── symbol_mappings.py
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
