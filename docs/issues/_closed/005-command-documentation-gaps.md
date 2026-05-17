# Raise Command README Quality

## Status

Resolved. The command README standard now lives in
`docs/command_documentation_guide.md`, and every public command package has a
local README that documents usage, options, examples, behavior notes, Python
entrypoints, and related commands.

## Problem

Most command packages included a local `README.md`, but the files were much
thinner than the command docstrings and parser contracts they were supposed to
explain. Several READMEs only contained a one-line summary, a command
invocation, and a short notes list. `proofstar2proof` and `proof2proofstar`
were also missing local READMEs entirely.

The result was that a user browsing a command package could not reliably
answer:

- what source form the command expects and what target form it writes;
- which syntax is deliberately preserved, ignored, or rejected;
- whether the command mutates files, writes backups, prints output, or only
  uses the clipboard;
- which options are supported and how they interact;
- when a reverse command is an alias for another command;
- what Python entrypoint exists for callers who want `transform_text(...)`.

## Desired Outcome

Every public command package should have a local `README.md` that is
user-facing, explicit about observable behavior and side effects, complete
enough for ordinary command use, and concise enough that the root README can
remain the command index.

The README standard should be promoted into
`docs/command_documentation_guide.md`, and the issue should stop being the
authoritative source for documentation rules.

## Resolution

- Added `docs/command_documentation_guide.md` with the accepted README shape,
  command-type guidance, reverse-alias guidance, configuration-file guidance,
  and naming policy.
- Linked the new guide from `docs/README.md`.
- Added missing local READMEs for `proofstar2proof` and `proof2proofstar`.
- Rewrote local READMEs for every public command package to document input
  forms, output forms, side effects, options, limits, realistic invocations,
  observable examples, Python APIs, and related commands.
- Kept the root README as a short command index instead of duplicating every
  per-command contract.
- Added no permanent tests because the change is documentation-only and does
  not alter observable command behavior.
