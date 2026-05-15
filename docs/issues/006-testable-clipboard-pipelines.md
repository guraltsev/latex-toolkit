# Make Clipboard Pipelines Testable Python Commands

## Status

Open.

## Problem

The clipboard workflows are currently batch scripts:

- `texmacs_latex_to_llm_latex.cmd`
- `llm_latex_to_texmacs_latex.cmd`
- `tm2tm.cmd`
- `snapper_format.cmd`

These scripts are useful operationally, but their sequencing, argument
validation, and failure behavior are not easy to exercise with ordinary Python
tests.

## Impact

Pipeline behavior can drift from individual command behavior without focused
test coverage. It is also harder to reuse the pipeline from Python or other
shells.

## Desired Outcome

Move pipeline orchestration into Python command packages and keep the `.cmd`
files as thin Windows launchers.

## Suggested Plan

1. Add Python command packages for the clipboard pipelines.
2. Represent each pipeline as an ordered list of existing `transform_text`
   callables or command functions.
3. Test pipeline ordering, argument validation, and stop-on-failure behavior
   through observable outcomes.
4. Update `.cmd` files to call the Python pipeline commands.

## Acceptance Criteria

- Pipeline behavior is covered by permanent observable tests.
- `.cmd` files contain only environment setup and command launching.
- Pipeline ordering is visible in Python code rather than duplicated in batch
  control flow.
