# Replace Implementation-Policy Tests With Observable Behavior Tests

## Status

Resolved. Permanent write-policy tests now exercise observable CLI and
clipboard behavior instead of source layout or helper imports.

## Problem

`docs/tests.md` says permanent tests should protect meaningful observable
behavior and should not preserve implementation details, file layout, module
boundaries, or refactoring choices.

Most tests follow this policy well. The main exception is
`tests/test_write_policy.py`, which inspects parser internals, source files,
package metadata, and imports. For example, it asserts that mutating commands
import `backup_file` from `lib.backup`. That is a design constraint, not a
user-visible contract.

## Impact

Implementation-policy tests make refactors harder, especially the command
package rename and library-boundary cleanup. They can fail even when user
behavior remains correct.

## Desired Outcome

Keep tests that exercise documented CLI behavior and remove tests that lock in
source layout or internal implementation choices.

## Suggested Plan

1. Convert write-policy checks into observable CLI tests where practical:
   overwrite behavior, backup creation, output-file behavior, clipboard mode,
   and concise errors.
2. Remove assertions about imports, package metadata, and absence of internal
   dispatchers.
3. Move non-observable architecture constraints into docs and issue notes.
4. Use temporary `tests/devel/` checks only during active refactors, then remove
   them before completion.

## Acceptance Criteria

- Permanent tests fail only for observable command or library regressions.
- Architecture constraints live in docs rather than permanent tests.
- The command package rename can proceed without tests preserving the old file
  layout.

## Resolution

- Replaced `tests/test_write_policy.py` with observable CLI and clipboard
  tests for overwrite behavior, backup creation, output aliases, no-backup
  mode, clipboard transformation, and concise parser errors.
- Documented the command write contract in `docs/development_guide.md`,
  including which details belong in tests and which belong in architecture
  guidance.
- Removed marker constants and alias-only backup imports that existed for the
  old implementation-policy tests.
