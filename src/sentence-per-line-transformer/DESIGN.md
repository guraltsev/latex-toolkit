# Sentence-per-line LaTeX formatter design

## Status

Proposed design only. The surrounding directory is an unchanged clone of the
LaTeX transformer template and provides the starting point for implementation.

## Goal

Format every prose paragraph so each sentence begins on its own physical source
line while preserving LaTeX meaning and all source outside the whitespace at an
identified sentence boundary.

Captions and footnotes are prose and must be formatted. A `\footnote{...}`
invocation is laid out as its own source-line block. Display math,
verbatim-like content, and comments are protected source: the formatter must
not indent, align, isolate, or otherwise rewrite them or their surrounding line
breaks. A protected display span is not itself a paragraph boundary.

The public `transform_text()`, file, and clipboard workflows remain those of
the template. The transformation must be idempotent.

## Observable contract

For ordinary prose:

```latex
First sentence. Second sentence.

Another paragraph. Its next sentence.
```

the result is:

```latex
First sentence.
Second sentence.

Another paragraph.
Its next sentence.
```

Paragraph separators remain separators. Existing line breaks inside a sentence
remain unchanged, including line breaks consumed by a `%` comment.

The motivating comment case is therefore:

```latex
This is the beginning %comment1
of a sentence. Now the next one starts %comment2
and ends.
```

and its exact result is:

```latex
This is the beginning %comment1
of a sentence.
Now the next one starts %comment2
and ends.
```

The comment text, percent marker, placement, and comment-terminating newline are
unchanged. Only the ordinary space between `sentence.` and `Now` is replaced.
The inserted newline has no trailing spaces.

Captions and footnotes follow the same sentence rule, and the footnote command
is placed on a separate source line:

```latex
\caption{First sentence. Second sentence.}
Text with a \footnote{First note sentence. Second note sentence.} Next sentence.
```

becomes:

```latex
\caption{First sentence.
Second sentence.}
Text with a
\footnote{First note sentence.
Second note sentence.}
Next sentence.
```

Putting an attached footnote on a new source line must not introduce a TeX
space before its mark. If the source has no whitespace before `\footnote`, the
layout rule inserts a comment-terminated newline (`%` followed by the input's
newline convention). Existing whitespace can be replaced by the newline
directly. The corresponding right edge must likewise preserve whether the
original source had whitespace, so punctuation immediately following a
footnote is not separated from it semantically.

Display math layout is not normalized. Each of these inputs is already in its
required output form and must remain byte-for-byte unchanged:

```latex
We obtain the following equation:
\[
1+1=2,
\]
where the numbers are defined using Peano's rules.
```

```latex
We obtain the following equation:
\[ 1+1=2, \]
where the numbers are defined using Peano's rules.
```

```latex
We obtain the following equation:  \[ 1+1=2, \] where the numbers are defined using Peano's rules.
```

In particular, the transform does not move `\[`, `\]`, or adjacent prose onto
separate lines. It does not join those lines either. Display math may interrupt
a prose sentence, as it does above, without making either side eligible for a
new sentence-boundary edit.

## Parser model and recursive span representation

`pylatexenc` 3 does not expose a paragraph node type. Its syntax tree contains
character, comment, macro, group, environment, specials, and math nodes. Every
node does expose source positions, and the parsing state can treat a double
newline as a distinct paragraph-break token. A `SpecialsSpec` for `"\n\n"` can
therefore make explicit blank-line breaks visible in a node list, but the
application must still group the surrounding nodes into logical paragraphs.

The implementation should represent prose scopes and their paragraph spans by
source offsets. These are application-level views over the parsed tree, not new
or mutated `pylatexenc` nodes. A scope may contain nested text-bearing scopes;
overlap is intentional and is resolved by processing children before parents.

A paragraph span contains the original source from its first prose token to its
last prose token, including inline macros, groups, inline or display math, and
comments. Display math is an opaque segment within the paragraph; it does not
end the paragraph merely because it is a block-level LaTeX construct.
Spans end at:

- a blank-line paragraph break;
- an explicit `\par`;
- the edge of a containing prose environment or text-bearing argument;
- a structural environment such as a table or verbatim content; or
- another structural boundary that snapper identifies as a separate block,
  such as a list item.

A single newline immediately before or after display math remains part of the
same paragraph and must be retained at its original source position. A blank
line still ends a paragraph by the ordinary blank-line rule; the neighboring
display is not what creates that boundary.

Paragraph discovery starts in each top-level `document` body. It recursively
enters prose-bearing environments and arguments, while treating verbatim-like
and structural block environments as opaque source. Display math instead stays
inside the surrounding paragraph as protected source. Captions and footnotes
are explicitly classified as text-bearing macros. Their mandatory text
arguments participate in paragraph discovery even when nested inside another
paragraph.

Nested prose is transformed depth first. For example, the text argument of an
inline `\footnote{...}` is formatted before the paragraph containing the
footnote. The resulting complete footnote invocation is then protected as an
immutable child span while the parent paragraph is formatted. The same rule
applies recursively to captions and other configured text-bearing arguments.

Processed child spans may not be sent through snapper again. The parent pass
uses stable opaque placeholders for them, restores their exact transformed
source afterward, and rejects output that duplicates, deletes, reorders, or
rewrites a placeholder. Thus the parent can format prose around a nested span
without reformatting the nested result.

## Formatting pipeline

1. Parse the complete source with `pylatexenc` and retain original source
   offsets.
2. Locate each top-level `document` environment. For a fragment without one,
   treat the complete input as a synthetic document body without changing the
   returned wrapper state.
3. Discover nested prose scopes and visit them in postorder. Within each scope,
   form paragraphs using real paragraph delimiters rather than display-math
   nodes. Do not enter verbatim-like blocks.
4. Format each deepest scope first. Apply the explicit footnote line-placement
   rule, then mark that transformed invocation as a protected child span in its
   parent.
5. For a parent paragraph, replace already processed child spans and protected
   display math with opaque placeholders. Send the resulting paragraph to
   `snapper-fmt` in LaTeX mode with `--max-width 0`, then restore the protected
   source exactly. Wrap a slice in a temporary document only when snapper
   requires document context, then remove only the known wrapper.
6. Validate the formatter result before accepting it: original comment lexemes
   must be identical and in the same order, protected math/verbatim slices must
   be unchanged, processed child spans must be restored exactly, and whitespace
   adjacent to display math must remain at the same source boundaries. A
   contract violation raises an error and leaves file or clipboard output
   untouched. Synthetic `%` markers introduced solely to preserve TeX spacing
   at a footnote line boundary are recorded separately and are not mistaken for
   changed input comments.
7. Return each transformed scope to its parent, updating parent-local offsets
   before the parent pass. This avoids conflicting edits from overlapping
   source spans and avoids whole-document AST recomposition.
8. Preserve the input newline convention and exact trailing newline run.

This design deliberately does not mutate `LatexCharsNode.chars` or use
`LatexNodesLatexRecomposer`. Source-span replacement limits changes to the
paragraphs snapper formatted and makes preservation requirements observable.

## Comments

A `LatexCommentNode` stores the comment separately from its
`comment_post_space`, which includes the terminating newline and following
indentation. Both pieces belong to the containing paragraph but are immutable
for this transform.

A comment does not end a sentence and does not end a paragraph. Sentence
detection must see prose on both sides of it as logically adjacent while the
source newline remains fixed. In the motivating case, the first comment is
inside the first sentence and the second comment is inside the second sentence;
neither comment is moved.

If snapper changes a comment or its terminating whitespace, paragraph
validation fails rather than silently accepting the rewrite. This behavior must
be established with a real-snapper integration test before implementation is
considered complete.

## Math and other protected content

Display math nodes and math environments (`equation`, `align`, their starred
forms, and configured equivalents) are opaque content within a paragraph, not
hard paragraph boundaries. They belong to the same logical paragraph as prose
on either side unless an ordinary paragraph delimiter such as a blank line or
`\par` intervenes.

Their entire original source slices and the contiguous non-blank-line
whitespace immediately before and after them are copied verbatim. In
particular, a preceding single newline remains exactly where it appeared. The
whitespace is part of the protected layout even when it consists only of
ordinary spaces on a prose line. Consequently, the formatter never adds
indentation to a display-math line, places a display on its own line, pulls it
into a prose line, or moves the prose on either side. Its role is
sentence-per-line formatting, not display-environment alignment.

Inline math remains inside its prose paragraph because it can occur in the
middle of a sentence. Its token text must remain byte-for-byte unchanged; only
ordinary whitespace after a completed sentence may be replaced.

Verbatim-like environments and commands are opaque. Tables and alignment
environments are initially treated as structural rather than prose. Prose in a
table cell can be added later only with an explicit, tested policy.

## Snapper boundary

Snapper is an external process boundary owned by a focused adapter. The adapter
is responsible for locating or installing the repository-local executable,
constructing the LaTeX command, wrapping fragments, restoring trailing
newlines, and turning nonzero exits into a clear `RuntimeError`.

Paragraph discovery remains local Python code because it defines this tool's
scope and preservation guarantees. Sentence detection and LaTeX-aware line
breaking remain snapper's responsibility.

Before relying on snapper output, add a development characterization test that
runs the real executable against comments, captions, footnotes, inline math,
and display math. If snapper cannot satisfy comment and protected-source
validation, stop and revise the adapter; do not add regex-based sentence
splitting as a fallback.

## Test plan

Permanent tests protect public `transform_text()` behavior using the real
parser and formatter. Mocking the subprocess is appropriate only for explicit
failure behavior; a mocked formatter cannot protect sentence splitting.

Each test below represents a user-visible regression:

- Two sentences in one paragraph become two physical lines.
- Multiple paragraphs are formatted independently and blank-line separators
  are preserved.
- Already formatted text is unchanged on a second pass.
- A sentence spanning a comment newline stays one sentence, while the following
  sentence starts on a new line exactly as in the motivating example.
- Comment spelling, placement, and terminating newlines are preserved exactly.
- Every sentence in `\caption{...}` and `\footnote{...}` starts on its own
  line.
- Every `\footnote{...}` invocation occupies its own source-line block without
  changing TeX spacing at either edge.
- Nested prose is formatted depth first, and a processed child span is
  byte-for-byte unchanged by all parent snapper passes.
- A display-math block and its adjacent whitespace are byte-for-byte unchanged;
  multiline, own-line compact, and prose-inline layouts remain exactly as
  supplied.
- Display math surrounded by single newlines remains inside one logical
  paragraph, so formatting resumes after it; only a real blank line or `\par`
  creates a paragraph boundary.
- Inline math is unchanged while surrounding sentence boundaries are split.
- Verbatim-like environments are unchanged.
- A fragment and a complete document both format correctly without leaking a
  temporary document wrapper.
- CRLF input retains CRLF output, and the exact trailing newline run is
  preserved.
- A snapper failure raises before a source file or clipboard value is changed.

The test module docstring must state that the real parser and snapper formatter
are used, with only filesystem and clipboard/process-failure boundaries mocked
where relevant. Test names and docstrings should describe these observable
contracts rather than paragraph-helper internals.

## Planned code changes

Implementation should remain command-specific in the cloned package:

- replace the example `DocumentTransformer` rule with paragraph discovery and
  source-span replacement in the main module;
- add a focused snapper process adapter near the workflow that consumes it;
- rename the package and console command only when implementation begins;
- add `snapper-fmt` to the install/runtime policy instead of hiding it behind an
  undeclared import; and
- update the cloned README after behavior exists.

No shared-library abstraction or persistent class hierarchy is warranted. A
small immutable paragraph-span value and direct narrated workflow are enough.

## Open implementation checks

- Record the exact snapper version used by tests and verify its executable name
  on Windows.
- Confirm snapper's placeholder handling for nested footnotes and captions,
  including nested processed spans and punctuation attached to a footnote.
- Define the initial complete list of verbatim-like and display-math
  environments.
- Decide whether section titles and other moving arguments should be formatted;
  they are not required by the current caption-and-footnote contract.
