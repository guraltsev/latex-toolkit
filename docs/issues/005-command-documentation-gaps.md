# Raise Command README Quality

## Status

Open.

## Problem

Most command packages include a local `README.md`, but the files are much
thinner than the command docstrings and parser contracts they are supposed to
explain. Several READMEs only contain a one-line summary, a command invocation,
and a short notes list. `proofstar2proof` and `proof2proofstar` are also
missing local READMEs entirely.

The result is that a user browsing a command package cannot reliably answer:

- what source form the command expects and what target form it writes;
- which syntax is deliberately preserved, ignored, or rejected;
- whether the command mutates files, writes backups, prints output, or only
  uses the clipboard;
- which options are supported and how they interact;
- when a reverse command is an alias for another command;
- what Python entrypoint exists for callers who want `transform_text(...)`.

## Impact

Users must read `main.py`, `transform.py`, root README snippets, and argparse
help to understand ordinary command behavior. The command packages also look
less owned during refactors because the local documentation does not capture
the public behavior that should remain stable.

## Desired Outcome

Every public command package should have a local `README.md` that is at least
as detailed in spirit as the public docstrings:

- user-facing rather than source-tour prose;
- explicit about observable behavior, side effects, guarantees, and limits;
- complete enough that ordinary users do not need to inspect Python docstrings
  to run the command correctly;
- concise enough that the root README can remain the command index rather than
  duplicating every detail.

The README format does not need to mirror NumPy-style docstrings. It should
translate the same public contract into task-oriented command documentation.

The proposal in this issue should be promoted into
`docs/command_documentation_guide.md` once the standard is accepted. After that
guide exists, this issue should track applying the guide to command READMEs
rather than remaining the authoritative source for the documentation rules.

## Proposed README Standard

Use this shape unless a command has a strong reason to differ.

````markdown
# `<package_name>`

One short paragraph stating the command's purpose, source syntax, and target
syntax. Mention the historical help label if it differs from the package name.

## Use Cases

- Common case where this command is the right tool.
- Any important reverse or pipeline relationship.

## Usage

```powershell
python -m latex_toolkit.commands.<package_name> .\paper.tex
python -m latex_toolkit.commands.<package_name> .\paper.tex -o .\paper.out.tex
python -m latex_toolkit.commands.<package_name> --clipboard
```

State whether the command supports file mode, clipboard mode, both, or only a
pipeline clipboard mode.

## Options

| Option | Meaning |
| --- | --- |
| `input` | Input path semantics, if supported. |
| `-o`, `--output`, `--output-file` | Output path behavior, if supported. |
| `--clipboard` | Clipboard behavior, if supported. |
| `-B`, `--no-backup` | Backup behavior, if supported. |
| command-specific option | Command-specific contract. |

Omit options the command does not expose.

## Examples

Show small before-and-after examples for mutating transforms, stdout examples
for reporting commands, and input/output clipboard examples for clipboard-only
pipelines.

## Behavior Notes

- What is deliberately converted.
- What is deliberately preserved.
- How comments, escaped syntax, nested environments, include paths, duplicate
  results, unmatched delimiters, or invalid options behave.
- Any external tool or configuration file requirements.

## Python API

Mention public callable entrypoints when useful, usually
`main.transform_text(...)`. For pipeline commands, mention whether the Python
API accepts configuration such as `macros_file`.

## Related Commands

List reverse commands, pipeline neighbors, or command-family siblings.
````

## Required Content By Command Type

File-transforming commands should document the shared write contract from
`docs/development_guide.md`: overwriting the input creates a timestamped
backup under `.backup`, `-o`/`--output` writes separately without a backup, and
`--clipboard` rejects simultaneous input or output paths.

Read-only reporting commands should say that they print to standard output and
do not rewrite source files. If clipboard mode is supported, document that the
clipboard is replaced with the rendered report.

Clipboard-only pipeline commands should make that constraint obvious near the
top. They should list each pipeline step in order, explain why the pipeline is
useful as a workflow, and document any configuration that is passed into an
inner step.

Reverse-alias commands should explicitly say which command they call and which
direction is forced. For example, `proof2proofstar` should be documented as
the reverse-direction alias for `proofstar2proof`, not as a separate parser
with independent behavior.

Commands with configuration files should include the minimal valid file shape,
path requirements, replacement-vs-extension semantics, and failure behavior
before input or clipboard contents are changed.

## Naming Policy

Use the importable package directory as the canonical README title and Python
module path, for example `strip_comments`. Mention historical dash spellings,
such as `strip-comments`, only as help/log labels or intentionally supported
wrappers.

## Suggested Plan

1. Adopt the README standard above as the target for this issue.
2. Create `docs/command_documentation_guide.md` from the accepted standard in
   this issue.
3. Link the new guide from `docs/README.md`.
4. Add missing READMEs for `proofstar2proof` and `proof2proofstar`.
5. Rewrite the clipboard pipeline READMEs first because they currently omit
   the most workflow context.
6. Rewrite command-family READMEs in pairs so direct and reverse commands agree
   on direction, shared guarantees, and aliases.
7. Finish with read-only and external-tool commands such as `list_graphics` and
   `snapper_format`, where stdout and dependency behavior need precise prose.
8. Keep the root README as the short command index, and link or summarize
   without trying to duplicate every per-command detail.

## Acceptance Criteria

- `docs/command_documentation_guide.md` exists and contains the accepted
  command README standard.
- `docs/README.md` links to `docs/command_documentation_guide.md`.
- Every public command package has a local README.
- Every README names the command's input form, output form, side effects,
  options, and limitations.
- Every README includes at least one realistic invocation and one observable
  example of output or before-and-after transformation.
- Root README and command READMEs agree on canonical command invocation.
- Historical aliases are documented only where they are intentionally
  supported.
- The documentation update does not add permanent tests, because this issue is
  documentation-only and does not change observable command behavior.

## Example Target: `texmacs_latex_to_llm_latex`

This command's README should say, in plain user-facing prose:

- it is clipboard-only;
- it prepares TeXmacs-generated LaTeX for LLM editing;
- it reads the system clipboard and replaces it with transformed text;
- it runs `dollar2bracket`, `ltae2aligned`, `tmscript2substack`,
  `proofstar2proof`, and `uni2tex` in that order;
- it has no input path, output path, backup, or configuration options;
- Python callers can use `main.transform_text(text)` to run the same ordered
  transforms without touching the clipboard;
- the reverse workflow is `llm_latex_to_texmacs_latex`.
