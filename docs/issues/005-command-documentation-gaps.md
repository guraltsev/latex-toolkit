# Fill Command Documentation Gaps

## Status

Open.

## Problem

Most command packages include a local `README.md`, but `proofstar2proof` and
`proof2proofstar` do not. The root README documents these commands, but the
per-command documentation pattern is incomplete.

## Impact

Users browsing command folders do not get the same local usage guidance for
every command. This also makes command ownership less clear during refactors.

## Desired Outcome

Every public command package should have local documentation matching the
repository's current command README pattern.

## Suggested Plan

1. Add local READMEs for `proofstar2proof` and `proof2proofstar`.
2. After the underscore package rename, make sure command README paths and
   invocation examples use the updated canonical package names or explicit
   compatibility aliases.
3. Keep the root README as the user-facing command index.

## Acceptance Criteria

- Every public command package has a local README.
- Root README and command READMEs agree on canonical command invocation.
- Historical aliases are documented only where they are intentionally
  supported.
