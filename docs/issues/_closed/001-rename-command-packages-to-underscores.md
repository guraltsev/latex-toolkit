# Rename Command Packages To Underscores

## Status

Resolved. The canonical source layout now uses underscore package names.

## Problem

`docs/development_guide.md` says command package directories use underscores,
not dashes. The source tree previously had dash-named Python package
directories, including command packages such as `strip-comments`,
`expand-includes`, `eqn-star2dmath`, `eqn2dmath-eqnum`,
`dmath2eqn-star`, and `dmath-eqnum2eqn`.

The README also presents dash spellings as the command package spelling. That
contradicts the guide's rule that user-facing historical or shell-facing names
may keep dash spellings, while source package directories should use valid
Python identifiers.

## Impact

Dash-named packages can be executed with `python -m`, but they are awkward for
normal Python imports and tooling. The repo had compensating machinery:

- `src/latex_toolkit/__init__.py` mutates `sys.path` and package `__path__` to
  support source-checkout command execution.
- Reverse-command aliases load sibling command modules with
  `importlib.util.spec_from_file_location(...)`.
- Tests currently normalize the dash layout instead of treating it as
  architecture debt.

## Desired Outcome

Use underscore package directories as the canonical source layout, including
`latex_toolkit` for the top-level Python package and command names such as
`strip_comments`, `expand_includes`, `eqn_star2dmath`,
`eqn2dmath_eqnum`, `dmath2eqn_star`, and `dmath_eqnum2eqn`.

Keep dash spellings only as user-facing compatibility shims when needed.

## Suggested Plan

1. Rename the top-level Python package and command package directories from
   dash names to underscore names.
2. Update `pyproject.toml`, package data, tests, README examples, and local
   launchers for the canonical underscore package path.
3. Update command imports so direct and reverse command families import each
   other normally.
4. Add thin compatibility packages, launchers, or documented aliases for the
   historical dash spellings if existing workflows depend on them.
5. Update README examples to distinguish canonical Python package names from
   shell-facing aliases.
6. Replace tests that enforce dash package layout with tests for documented
   invocation behavior.

## Acceptance Criteria

- Source Python package directories use only valid Python identifiers.
- Direct/reverse command aliases use normal imports instead of file-location
  imports.
- Existing documented command invocations either still work through explicit
  compatibility shims or are intentionally updated in README and command docs.
- The full test suite passes.

## Resolution

- Renamed the top-level source package to `latex_toolkit`.
- Renamed dash-named command packages to underscore identifiers, including
  `strip_comments`, `expand_includes`, `list_graphics`,
  `eqn_star2dmath`, `eqn2dmath_eqnum`, `dmath2eqn_star`, and
  `dmath_eqnum2eqn`.
- Updated command imports, metadata, README examples, command docs, local
  launchers, and tests to use canonical underscore module paths.
- Kept historical dash spellings as user-facing command labels in help text
  and log messages where those names already existed.
