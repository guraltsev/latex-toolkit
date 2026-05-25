# `ref_to_cref`

`ref_to_cref` rewrites a narrow set of singular named `\ref` phrases into
direct `\cref` or `\Cref` calls.

## Supported rewrites

- `Proposition~\ref{prop:...}` and `Proposition \ref{prop:...}` become
  `\Cref{prop:...}`.
- `proposition~\ref{prop:...}` and `proposition \ref{prop:...}` become
  `\cref{prop:...}`.
- The same capitalization-sensitive rewrite applies to `Lemma`, `Corollary`,
  `Theorem`, and `Remark` with only these eligible label prefixes:
  `lem:`, `lemma:`, `cor:`, `corr:`, `corrollary:`, `theorem:`, `thm:`,
  `rmk:`, and `rem:`.

Plural phrases, other noun spellings, and labels with other prefixes are left
unchanged.
