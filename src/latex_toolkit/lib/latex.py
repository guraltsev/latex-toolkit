"""Helpers for lightweight LaTeX source inspection and rewriting.

The helpers in this module intentionally cover common text-based workflows.
They do not attempt to be a complete TeX parser.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from .core import TexFile, read_tex_file, write_tex_file

# Include commands that can be resolved and expanded by the toolkit.
INCLUDE_RE = re.compile(
    r"\\(?P<kind>input|include|subfile|subfileinclude)\s*\{(?P<target>[^{}]+)\}"
)

# Graphics targets are reported without attempting to resolve file paths.
GRAPHICS_RE = re.compile(r"\\includegraphics(?:\s*\[[^\]]*\])?\s*\{(?P<target>[^{}]+)\}")

# Full-line includes can preserve the surrounding line ending more naturally.
FULL_LINE_INCLUDE_RE = re.compile(
    r"^\s*\\(?P<kind>input|include|subfile|subfileinclude)\s*\{(?P<target>[^{}]+)\}\s*$"
)

# Subfile inclusion keeps only the child document body when markers are present.
BEGIN_DOCUMENT_RE = re.compile(r"\\begin\s*\{document\}")
END_DOCUMENT_RE = re.compile(r"\\end\s*\{document\}")
SUBFILE_COMMANDS = {"subfile", "subfileinclude"}


class IncludeCycleError(RuntimeError):
    """Raised when include expansion detects a recursive include cycle."""


@dataclass(frozen=True, slots=True)
class IncludeReference:
    """Describe a supported include command found in TeX source.

    Parameters
    ----------
    kind : str
        Include command name without the leading backslash.
    target : str
        Raw include target captured from the command argument.

    Attributes
    ----------
    kind : str
        Include command name without the leading backslash.
    target : str
        Raw include target captured from the command argument.
    """

    kind: str
    target: str


def read_text(path: str | Path) -> str:
    """Read a TeX file from disk as UTF-8 text.

    Parameters
    ----------
    path : str or pathlib.Path
        File path to expand, resolve, and read.

    Returns
    -------
    str
        Contents of the TeX file.
    """

    return read_tex_file(path).code


def write_text(path: str | Path, content: str) -> None:
    """Write UTF-8 text to a TeX file path.

    Parent directories are created as needed.

    Parameters
    ----------
    path : str or pathlib.Path
        Destination path to expand and resolve before writing.
    content : str
        Text to write.

    Returns
    -------
    None
        The destination file is replaced with ``content``.
    """

    write_tex_file(TexFile(content, None), path)


def _line_ending(fragment: str) -> str:
    if fragment.endswith("\r\n"):
        return "\r\n"
    if fragment.endswith("\n"):
        return "\n"
    if fragment.endswith("\r"):
        return "\r"
    return ""


def _split_trailing_line_ending(fragment: str) -> tuple[str, str]:
    ending = _line_ending(fragment)
    if not ending:
        return fragment, ""
    return fragment[: -len(ending)], ending


def split_comment(line: str) -> tuple[str, str]:
    """Split a line into code and comment parts.

    A percent sign starts a comment only when preceded by an even number of
    consecutive backslashes.

    Parameters
    ----------
    line : str
        Single source line, with or without a trailing line ending.

    Returns
    -------
    tuple of str
        Pair ``(code, comment)``. ``comment`` is empty when the line has no
        unescaped percent comment.
    """

    for index, char in enumerate(line):
        if char != "%":
            continue

        backslashes = 0
        lookback = index - 1
        while lookback >= 0 and line[lookback] == "\\":
            backslashes += 1
            lookback -= 1

        if backslashes % 2 == 0:
            return line[:index], line[index:]

    return line, ""


def strip_comments_from_line(line: str) -> str:
    """Remove an unescaped percent comment from one line.

    Escaped percent signs are preserved, and a removed comment's line ending is
    kept so the surrounding line structure remains stable.

    Parameters
    ----------
    line : str
        Single source line, with or without a trailing line ending.

    Returns
    -------
    str
        Line with the comment body removed.
    """

    code, comment = split_comment(line)
    if not comment:
        return line
    return code + _line_ending(comment)


def strip_comments_from_text(text: str) -> str:
    """Remove unescaped percent comments from LaTeX source text.

    Parameters
    ----------
    text : str
        LaTeX source text to strip.

    Returns
    -------
    str
        Source text with comment bodies removed and original line endings
        preserved.
    """

    return "".join(strip_comments_from_line(line) for line in text.splitlines(keepends=True))


def resolve_tex_input(base_file: str | Path, target: str) -> Path:
    """Resolve an include target relative to a TeX file.

    Targets without a suffix are tried both as written and with a ``.tex``
    suffix.

    Parameters
    ----------
    base_file : str or pathlib.Path
        Including file whose parent directory anchors relative targets.
    target : str
        Raw include target captured from an include command.

    Returns
    -------
    pathlib.Path
        Resolved path to an existing include file.

    Raises
    ------
    ValueError
        ``target`` is empty after stripping whitespace.
    FileNotFoundError
        No candidate include file exists.
    """

    base_path = Path(base_file).expanduser().resolve()
    raw_target = target.strip()
    if not raw_target:
        raise ValueError(f"Empty include target found in {base_file}")

    candidate = (base_path.parent / raw_target).expanduser()
    choices = [candidate]
    if candidate.suffix == "":
        choices.append(candidate.with_suffix(".tex"))

    for choice in choices:
        if choice.exists() and choice.is_file():
            return choice.resolve()

    expected = ", ".join(str(path) for path in choices)
    raise FileNotFoundError(
        f"Could not resolve include target {target!r} from {base_file}. Tried: {expected}"
    )


def extract_include_references(text: str) -> list[IncludeReference]:
    """Extract supported include commands from uncommented TeX source.

    Parameters
    ----------
    text : str
        LaTeX source text to inspect.

    Returns
    -------
    list of IncludeReference
        Include commands in source order, excluding commands that appear only
        inside comments.
    """

    references: list[IncludeReference] = []
    for line in text.splitlines(keepends=True):
        code, _comment = split_comment(line)
        body, _ending = _split_trailing_line_ending(code)
        references.extend(
            IncludeReference(kind=match.group("kind"), target=match.group("target"))
            for match in INCLUDE_RE.finditer(body)
        )
    return references


def extract_include_targets(text: str) -> list[str]:
    """Extract supported include targets from uncommented TeX source.

    Parameters
    ----------
    text : str
        LaTeX source text to inspect.

    Returns
    -------
    list of str
        Raw include targets in source order.
    """

    return [reference.target for reference in extract_include_references(text)]


def _extract_subfile_body(text: str) -> str | None:
    r"""Return the included body of a ``subfiles`` child, if recognizable.

    When a subfile is loaded from the main document, the subfiles package ignores
    the subfile preamble up to ``\begin{document}`` and ignores
    ``\end{document}`` and everything after it. If no begin marker is found, the
    caller should fall back to the original text.
    """

    started = False
    parts: list[str] = []

    for line in text.splitlines(keepends=True):
        code, comment = split_comment(line)
        body, ending = _split_trailing_line_ending(code)

        if not started:
            begin_match = BEGIN_DOCUMENT_RE.search(body)
            if begin_match is None:
                continue
            started = True
            remainder = body[begin_match.end() :]
            if remainder or comment:
                parts.append(remainder + ending + comment)
            continue

        end_match = END_DOCUMENT_RE.search(body)
        if end_match is not None:
            prefix = body[: end_match.start()]
            if prefix:
                parts.append(prefix)
            return "".join(parts)

        parts.append(body + ending + comment)

    if not started:
        return None
    return "".join(parts)


def _effective_tex_file(tex_file: TexFile, include_kind: str | None) -> TexFile:
    if include_kind not in SUBFILE_COMMANDS:
        return tex_file

    subfile_body = _extract_subfile_body(tex_file.code)
    if subfile_body is None:
        return tex_file
    return TexFile(code=subfile_body, filename=tex_file.filename)


def _coerce_to_tex_file(source: str | Path | TexFile) -> TexFile:
    if isinstance(source, TexFile):
        return source
    return read_tex_file(source)


def _require_filename(tex_file: TexFile) -> Path:
    if tex_file.filename is None:
        raise ValueError("This operation requires a named TeX file.")
    return tex_file.filename


def walk_tex_documents(root_file: str | Path | TexFile) -> list[TexFile]:
    """Return the root document and reachable include documents in visit order.

    Subfile includes contribute only their document body when recognizable.
    Files already visited through another include edge are returned once.

    Parameters
    ----------
    root_file : str, pathlib.Path, or TexFile
        Root TeX file path or named source buffer to inspect.

    Returns
    -------
    list of TexFile
        Named source buffers in root-first traversal order.

    Raises
    ------
    ValueError
        ``root_file`` or a reachable buffer has no filename metadata.
    FileNotFoundError
        A reachable include target cannot be resolved.
    """

    root_tex = _coerce_to_tex_file(root_file)
    visited: set[Path] = set()
    ordered: list[TexFile] = []

    def visit(current: TexFile, include_kind: str | None) -> None:
        resolved = _require_filename(current).resolve()
        if resolved in visited:
            return
        visited.add(resolved)

        effective = _effective_tex_file(current, include_kind)
        ordered.append(effective)
        for reference in extract_include_references(effective.code):
            child_path = resolve_tex_input(resolved, reference.target)
            visit(read_tex_file(child_path), reference.kind)

    visit(root_tex, None)
    return ordered


def walk_tex_sources(root_file: str | Path | TexFile) -> list[Path]:
    """Return resolved source paths reachable from a root TeX document.

    Parameters
    ----------
    root_file : str, pathlib.Path, or TexFile
        Root TeX file path or named source buffer to inspect.

    Returns
    -------
    list of pathlib.Path
        Resolved source paths in root-first traversal order.

    Raises
    ------
    ValueError
        ``root_file`` or a reachable buffer has no filename metadata.
    FileNotFoundError
        A reachable include target cannot be resolved.
    """

    return [_require_filename(tex_file).resolve() for tex_file in walk_tex_documents(root_file)]


def expand_includes(root_file: str | Path | TexFile) -> TexFile:
    """Inline supported include commands into one anonymous TeX buffer.

    Full-line includes preserve surrounding line endings and trailing comments
    where possible. Subfile includes contribute only their document body when
    recognizable.

    Parameters
    ----------
    root_file : str, pathlib.Path, or TexFile
        Root TeX file path or named source buffer to expand.

    Returns
    -------
    TexFile
        Anonymous buffer containing the expanded source text.

    Raises
    ------
    ValueError
        ``root_file`` or a reachable buffer has no filename metadata.
    FileNotFoundError
        A reachable include target cannot be resolved.
    IncludeCycleError
        Include expansion encounters a recursive include cycle.
    """

    root_tex = _coerce_to_tex_file(root_file)

    def expand_file(current: TexFile, stack: tuple[Path, ...], include_kind: str | None) -> str:
        resolved = _require_filename(current).resolve()
        if resolved in stack:
            cycle = " -> ".join(str(path) for path in (*stack, resolved))
            raise IncludeCycleError(f"Include cycle detected: {cycle}")

        effective = _effective_tex_file(current, include_kind)
        out_parts: list[str] = []
        next_stack = (*stack, resolved)

        def replace_match(match: re.Match[str]) -> str:
            child_path = resolve_tex_input(resolved, match.group("target"))
            child_tex = read_tex_file(child_path)
            return expand_file(child_tex, next_stack, match.group("kind"))

        for line in effective.code.splitlines(keepends=True):
            code, comment = split_comment(line)
            body, line_ending = _split_trailing_line_ending(code)

            full_line_match = FULL_LINE_INCLUDE_RE.fullmatch(body)
            if full_line_match is not None:
                child_path = resolve_tex_input(resolved, full_line_match.group("target"))
                child_tex = read_tex_file(child_path)
                expanded_child = expand_file(child_tex, next_stack, full_line_match.group("kind"))
                if line_ending and not expanded_child.endswith(("\n", "\r")):
                    expanded_child += line_ending
                out_parts.append(expanded_child + comment)
                continue

            expanded_body = INCLUDE_RE.sub(replace_match, body)
            out_parts.append(expanded_body + line_ending + comment)

        return "".join(out_parts)

    return TexFile.anonymous(expand_file(root_tex, (), None))


def extract_graphics_targets(text: str) -> list[str]:
    """Extract ``includegraphics`` targets from uncommented TeX source.

    Parameters
    ----------
    text : str
        LaTeX source text to inspect.

    Returns
    -------
    list of str
        Raw graphics targets in source order.
    """

    results: list[str] = []
    for line in text.splitlines(keepends=True):
        code, _comment = split_comment(line)
        body, _ending = _split_trailing_line_ending(code)
        results.extend(match.group("target") for match in GRAPHICS_RE.finditer(body))
    return results
