# `mdt_full_normalize`

`mdt_full_normalize` canonically formats a deliberately small MyST Markdown
dialect.  It composes prose whitespace regularization, `\\(...\\)` to `$...$`
conversion, line-oriented `\\[...\\]` to `$$...$$` conversion, TeX math
bracing, and conservative sentence-per-line prose formatting.

It uses MyST (`myst-parser`) on a CommonMark base.  TeX math is the selected
extension; GFM tables, task lists, and strikethrough are intentionally opaque
until a canonical renderer policy is added.

Only ordinary paragraphs and atx headings receive layout changes.  YAML/TOML
front matter, fences and indented code, inline code, HTML, links and image
destinations/titles, reference definitions, tables, thematic breaks, lists,
block quotes, setext headings, hard breaks, and all existing math content are
preserved exactly.  The delimiter command changes only the delimiters, and it
converts display delimiters only when `\\[` and `\\]` appear on otherwise
blank lines.  Unsupported or malformed source is left opaque.

Sentence boundaries are ASCII `.`, `!`, or `?`, optionally followed by closing
quotes/brackets, then whitespace or paragraph end.  Abbreviations, decimals,
initials, and non-English punctuation are known limitations.
