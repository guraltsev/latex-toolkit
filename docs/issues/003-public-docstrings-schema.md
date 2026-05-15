# Bring Public Docstrings Up To Schema

## Status

Open.

## Problem

`docs/docstring_schema.md` requires public functions, methods, and classes to
use NumPy-style docstring sections for public parameters, return values, and
intentional exceptions. The repository has good module docstring coverage, but
many public callables still use brief one-line docstrings or no callable
docstring at all.

Examples include command `build_parser(...)` and `main(...)` functions across
the command packages, plus public helpers in `lib/latex.py` such as
`read_text(...)`, `write_text(...)`, `strip_comments_from_text(...)`,
`resolve_tex_input(...)`, `walk_tex_documents(...)`, `expand_includes(...)`,
and `extract_graphics_targets(...)`.

## Impact

The API contracts are less clear than the guide requires. This is especially
noticeable around command entrypoints, public text transforms, file side
effects, and helper functions that raise operational errors.

## Desired Outcome

Public docstrings should describe contracts rather than source tours, and
should include required NumPy-style sections where the schema calls for them.

## Suggested Plan

1. Start with public functions in `lib`, since those are most likely to be used
   by callers and command modules.
2. Add concise `Parameters`, `Returns`, and `Raises` sections where required.
3. Normalize command `build_parser(...)`, `transform_text(...)`, and
   `main(...)` docstrings after the command package rename settles.
4. Avoid expanding private helper docstrings unless the helper has non-obvious
   internal behavior.

## Acceptance Criteria

- Public callables follow `docs/docstring_schema.md`.
- Docstrings describe observable behavior, inputs, outputs, side effects,
  guarantees, and intentional exceptions.
- No docstrings use source-navigation language forbidden by the schema.
