# Markdown Support Feasibility Report

## Decision

The toolkit can usefully support Markdown through a MyST-aware
`mdt_full_normalize` command. It is the Markdown-tool counterpart to the
existing LaTeX normalizer: each remains format-specific and composes only
reasonable transformations for its own source format.

The first useful release introduces `mdt_full_normalize`. It formats ordinary
Markdown prose one sentence per physical source line, produces deterministic
canonical whitespace, converts TeX command math delimiters from `\(...\)` and
`\[...\]` to `$...$` and `$$...$$`, and leaves syntax-sensitive content safe.
The pipeline can later gain further Markdown-specific transformations only when
their contracts are clear.

This is an adaptation of the toolkit's preservation-oriented product goal, not
a conversion from LaTeX documents to Markdown. Markdown may contain TeX math,
but headings, links, lists, code, front matter, HTML, and block structure have
different semantics from TeX environments and macros.

## What Can Be Reused

| Existing component | Reuse decision | Reason |
| --- | --- | --- |
| `lib.backup.backup_file` | Reuse unchanged | Backup-before-overwrite is syntax-independent. |
| `lib.streams.configure_utf8_standard_streams` | Reuse unchanged | UTF-8 stdin/stdout applies to `.md` inputs. |
| `lib.dependencies.DependencyManager` | Reuse unchanged | It can load a Markdown parser dependency at the command boundary. |
| File, output, clipboard, and stdin semantics | Reuse as a command contract | Commands already have a consistent observable interface. |
| Idempotent, deterministic transformations | Reuse as a product contract | Canonical whitespace makes repeated runs stable and Git diffs uniform. |
| `math_latex2dollar.transform_text` | Do not call directly | Its output mapping is right, but its `pylatexenc` boundary is not Markdown-aware. |

The development guide reserves `lib/` for meaningful shared code. If both
proposed Markdown commands need the same block and inline span model,
`lib/markdown.py` is justified as shared parsing infrastructure. A one-command
prototype should keep Markdown-specific code in that command package until a
second consumer exists.

## Existing Command Compatibility

| Command or layer | Markdown suitability | Required adaptation |
| --- | --- | --- |
| `sentence_per_line` | Conceptually useful; implementation cannot be reused | Replace TeX parsing, macro recursion, TeX comments, and `snapper --format latex` with Markdown block/inline discovery and a Markdown-aware formatter. |
| `math_latex2dollar` | Desired transform, unsafe implementation | Select command-delimited math only in Markdown text, then replace delimiters only. |
| `math_dollar2latex` | Not a Markdown default | `$` and `$$` are common Markdown-math syntax, so converting away from them is counterproductive. |
| `full_normalize` | Reuse as the model for the Markdown entrypoint | Preserve its LaTeX stages exactly; implement the Markdown stages in the new `mdt_full_normalize` command. |
| `syntax_regularizer` | Not reusable | LaTeX indentation, environments, `\item`, and section macros do not correspond to Markdown grammar. |
| `brace_args` | Applicable inside Markdown math only | Reuse it on each parser-identified TeX math span, never on surrounding Markdown source. |
| `eqnum_label` | Not applicable by default | Markdown has no portable equivalent of TeX `\label` or `\eqnum`. |
| Greek converters | Potentially reusable only at the mapping level | Reimplement math-span selection for Markdown, then reuse or extract the character-to-macro mappings. |
| `template` | Not reusable as a Markdown template | It is a `pylatexenc` tree visitor and teaches the wrong extension boundary. |

All current syntax-sensitive commands invoke `pylatexenc` and assume either a
LaTeX fragment or a top-level `document` environment. That is the principal
technical boundary: a Markdown file passed through these parsers can have code
fences, escapes, link destinations, YAML front matter, and raw HTML
misclassified or rewritten.

## Required Markdown Contract

Use `myst-parser` as the primary Markdown parsing dependency. It provides a
MyST-configured `markdown-it-py` parser and token stream, so it recognizes
CommonMark structure plus MyST directives and roles without treating those
constructs as ordinary prose. Configure its parser deliberately for the
project's enabled MyST features rather than accepting every extension by
default. The target dialect is MyST on a CommonMark base, with explicit
GitHub-Flavored Markdown (GFM) extensions for tables, task-list items, and
strikethrough where the selected parser configuration supports them. Math is
not part of CommonMark or core GFM, so documentation must state the selected
TeX-math extension.

For `mdt_full_normalize`, initially format prose in paragraph text. Atx
headings, list-item paragraphs, and block-quote paragraphs can be added only
after their source-prefix behavior is explicitly specified and tested.

Preserve these regions exactly in the first release:

- YAML/TOML front matter;
- fenced and indented code blocks, plus inline code spans;
- raw HTML blocks, inline HTML, and HTML comments;
- link/image destinations, titles, reference definitions, and autolinks;
- tables, thematic breaks, list markers and continuation indentation;
- block quotes until their continuation-prefix behavior is deliberately added;
- setext headings, hard line breaks (two trailing spaces or a trailing
  backslash), and lines whose joining could change Markdown block parsing; and
- `$...$`, `$$...$$`, `\(...\)`, and `\[...\]` math spans, including contents.

The formatter may replace only soft line breaks inside one accepted prose
block. It joins wrapping within a sentence with one space, replaces whitespace
at a detected sentence boundary with the file's existing newline convention,
preserves paragraph separators and trailing newline runs, and is idempotent.
It must never join across Markdown block boundaries.

Sentence detection needs an explicit policy. Reusing Snapper would make results
dependent on a LaTeX formatter and cannot protect Markdown structure. Use a
local sentence-boundary component, initially with conservative ASCII terminal
punctuation (`.`, `!`, `?`) followed by closing quote/bracket characters and
whitespace or end of prose. Abbreviations, decimals, initials, and non-English
punctuation should be documented limitations rather than silently guessed.

## Math-Delimiter Conversion Contract

The requested direction is a good narrowly scoped command:

```markdown
Inline \(x + 1\) becomes $x + 1$.

\[
x + 1
\]
becomes

$$
x + 1
$$
```

The command should change delimiter characters only; it must preserve math
content and surrounding source. It should recognize delimiters only in
ordinary Markdown prose and later-supported heading/list/quote text, never in
protected regions. In version one, require `\[` and `\]` to occur on otherwise
blank lines (apart from allowed indentation) before translating them to `$$`
lines. That conservative rule avoids creating ambiguous inline or
paragraph-breaking Markdown.

Do not infer dollar math from arbitrary dollar signs in the reverse direction.
Currency, shell examples, and code-like prose make `$...$` detection dialect-
and context-dependent. If a reverse command is added, define and test its
delimiter rules independently.

## Recommended Architecture

Use `myst-parser` as the syntax authority, then render a deterministic,
documented Markdown layout for the supported dialect. The intended contract is
semantic preservation plus canonical, idempotent formatting; retaining every
harmless original space or line ending is not a goal. The implementation must
still preserve syntax-sensitive content, such as code, directive bodies, link
destinations, and raw HTML, according to the command's documented policy.

1. Parse with `myst-parser` and use its MyST-configured `markdown-it-py` token
   stream as the authoritative block and inline classification. Validate that
   its tokens cover every supported construct before formatting it.
2. Build a canonical Markdown renderer for the supported token kinds. It may
   normalize harmless whitespace, line endings, and soft wraps, but it must
   retain the semantics and documented spelling of code, directives, links,
   math contents, front matter, and raw HTML.
3. Treat unsupported token kinds as opaque and reproduce them unchanged until
   a canonical rendering policy is deliberately added. This is a scope choice,
   not an invitation to reimplement Markdown grammar with regular expressions.
4. Require the renderer to be idempotent: a second run produces identical
   output. Use the same canonical newline convention throughout its output.

Declare `myst-parser` in `pyproject.toml` for a first-class command and add it
to the command's `DependencyManager` mapping. This retains current toolkit
behavior: importing a module has no side effects, while invoking a transform or
CLI command automatically installs a missing configured dependency. The parser
and canonical renderer limit support to the declared dialect; uncertain or
unsupported constructs remain opaque.

## Markdown Command Shape

Use `mdt_` as the user-facing namespace for every Markdown-capable tool, in
parallel with the existing `lt_*.cmd` wrappers. Each command receives a console
script and an `src/mdt_<name>.cmd` wrapper, uses the same file, clipboard, and
stdin contract as its LaTeX counterpart, and never needs `--format` or file
extension inference: its `mdt_` name selects MyST/Markdown.

| Markdown command | Markdown-specific behavior |
| --- | --- |
| `mdt_full_normalize` | Compose the applicable `mdt_` transforms into canonical MyST normalization. |
| `mdt_sentence_per_line` | Put supported Markdown prose sentences on physical source lines. |
| `mdt_syntax_regularizer` | Apply canonical Markdown block and whitespace layout without TeX environment rules. |
| `mdt_math_latex2dollar` | Convert `\(...\)`/`\[...\]` to `$...$`/`$$...$$` only in identified math. |
| `mdt_math_dollar2latex` | Optional reverse interoperability command; never part of `mdt_full_normalize`. |
| `mdt_brace_args` | Apply existing TeX bracing logic only inside identified math spans. |
| `mdt_greek_unicode2latex` and `mdt_greek_latex2unicode` | Apply the existing conversions only inside identified math spans. |

`mdt_full_normalize` composes `mdt_syntax_regularizer`,
`mdt_math_latex2dollar`, `mdt_brace_args`, and `mdt_sentence_per_line` in an
order established by their tests. It must not include `eqnum_label`, because
TeX equation-label placement has no portable Markdown equivalent.

An `mdt_template` command can be added when there is a concrete MyST AST
transformation template to offer; it should not reuse the `pylatexenc` visitor.
Keep the Markdown-specific implementations in their command packages
initially. Extract `lib/markdown.py` only when multiple `mdt_` commands need
the same MyST parsing and rendering infrastructure.

## Delivery Plan

1. Write the dialect and preservation matrix in the command README, including
   the exact `$`/`$$` renderer expectation. Safest version one: plain
   paragraphs plus atx headings.
2. Build a small `myst-parser` rendering spike with MyST, CommonMark, and GFM
   fixtures. Verify that its token stream classifies each supported construct
   and that a second render is byte-identical to the first.
3. Implement shared MyST parse/classification support as the first reusable
   Markdown building block.
4. Implement `mdt_math_latex2dollar` and `mdt_brace_args`; their narrow,
   math-only contracts prove protected-region selection.
5. Implement `mdt_sentence_per_line` and `mdt_syntax_regularizer` with the
   same parser-backed model. Do not invoke Snapper.
6. Add the Greek converters where the shared math-span selection makes their
   existing mapping logic applicable.
7. Compose the completed applicable stages in `mdt_full_normalize` after their
   idempotence and semantic preservation are established.

## Test Matrix

Permanent tests should follow `docs/tests.md`: assert observable canonical
source, not parser internals. Add fixtures and tests for at least:

- wrapped paragraphs, sentence boundaries, paragraph breaks, `LF`/`CRLF`,
  trailing newlines, and idempotence;
- atx headings and the selected list/block-quote behavior;
- backtick and tilde fences, indented code, and variable-length inline code;
- YAML front matter, HTML comments/blocks, autolinks, links/images, reference
  definitions, escaped punctuation, and tables;
- inline/display TeX math, multiline displays, math beside prose, and `\(` or
  `\[` spellings inside every protected region;
- bracing of implicit TeX macro arguments and math scripts inside supported
  inline and display math, without changes to identical Markdown prose; 
- dollar-like non-math text such as currency and shell snippets;
- file overwrite backup, `--output`, clipboard, and `--stdin`; and
- unsupported or malformed input remaining unchanged rather than receiving a
  partial rewrite.

## Risks and Non-Goals

Markdown is extensible, and renderer math behavior differs among GitHub,
MkDocs, MyST, and static-site plugins. The command must name its supported
dialect instead of claiming universal Markdown support.

Do not promise a semantic-preserving Markdown pretty-printer, LaTeX-to-
Markdown conversion, citation conversion, reference-link rewriting, or safe
rewriting of arbitrary embedded HTML in the first release. Unsupported
extensions should be opaque. This fail-closed policy matches current LaTeX
commands, which return incomplete input unchanged rather than attempt unsafe
slicing.
