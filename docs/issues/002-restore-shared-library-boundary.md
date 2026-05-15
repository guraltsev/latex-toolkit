# Restore The Shared Library Boundary

## Status

Open.

## Problem

`docs/development_guide.md` says `src/latex_toolkit/lib/` is for meaningful
shared code and should not receive command-specific behavior merely to shorten
command files or simplify imports.

The current `lib` package contains true shared infrastructure, such as backup
policy, clipboard boundaries, source I/O, and LaTeX tokenization. It also
contains many command-family transforms, including `aligned_baea.py`,
`dollar_delimiters.py`, `equation_star_displaymath.py`,
`equation_eqnum_displaymath.py`, `ltae_aligned.py`, `proofstar.py`,
`texmacs_aligned_ltae.py`, `tmscript_substack.py`, and
`unary_macro_bracing.py`.

## Impact

The boundary between reusable toolkit infrastructure and command-owned
behavior is blurred. This makes it harder to tell which APIs are public shared
building blocks and which are implementation details of a command family.

## Desired Outcome

Keep durable shared infrastructure in `lib`, and colocate command-family
transforms with the commands that own them unless the code is genuinely reused
across unrelated command families.

## Suggested Plan

1. Classify each `lib` module as shared infrastructure, shared transform API,
   or command-family implementation.
2. Move command-family implementation modules near their owning command
   packages after the underscore package rename is in place.
3. Keep direct and reverse commands importing from each other within the same
   command family.
4. Document any intentional public transform APIs that remain in `lib`.

## Acceptance Criteria

- `lib` contains only shared infrastructure or intentionally documented public
  Python building blocks.
- Command-family transforms live near their command families.
- Imports are normal Python imports.
- Tests continue to cover observable transform and CLI behavior.
