"""Helpers for lightweight LaTeX source inspection and rewriting.

The helpers in this module intentionally cover common text-based workflows.
They do not attempt to be a complete TeX parser.
"""

from __future__ import annotations

from pathlib import Path
import re

INCLUDE_RE = re.compile(r"\\(?P<kind>input|include)\s*\{(?P<target>[^{}]+)\}")
GRAPHICS_RE = re.compile(r"\\includegraphics(?:\s*\[[^\]]*\])?\s*\{(?P<target>[^{}]+)\}")
FULL_LINE_INCLUDE_RE = re.compile(r"^\s*\\(?P<kind>input|include)\s*\{(?P<target>[^{}]+)\}\s*$")


class IncludeCycleError(RuntimeError):
    """Raised when include expansion detects a recursive include cycle."""


def read_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def write_text(path: str | Path, content: str) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")


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
    code, comment = split_comment(line)
    if not comment:
        return line
    return code + _line_ending(comment)


def strip_comments_from_text(text: str) -> str:
    return "".join(strip_comments_from_line(line) for line in text.splitlines(keepends=True))


def resolve_tex_input(base_file: str | Path, target: str) -> Path:
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


def extract_include_targets(text: str) -> list[str]:
    targets: list[str] = []
    for line in text.splitlines(keepends=True):
        code, _comment = split_comment(line)
        body, _ending = _split_trailing_line_ending(code)
        targets.extend(match.group("target") for match in INCLUDE_RE.finditer(body))
    return targets


def walk_tex_sources(root_file: str | Path) -> list[Path]:
    root_path = Path(root_file).expanduser().resolve()
    visited: set[Path] = set()
    ordered: list[Path] = []

    def visit(current: Path) -> None:
        resolved = current.resolve()
        if resolved in visited:
            return
        visited.add(resolved)
        ordered.append(resolved)
        content = read_text(resolved)
        for target in extract_include_targets(content):
            visit(resolve_tex_input(resolved, target))

    visit(root_path)
    return ordered


def expand_includes(root_file: str | Path) -> str:
    root_path = Path(root_file).expanduser().resolve()

    def expand_file(current: Path, stack: tuple[Path, ...]) -> str:
        resolved = current.resolve()
        if resolved in stack:
            cycle = " -> ".join(str(path) for path in (*stack, resolved))
            raise IncludeCycleError(f"Include cycle detected: {cycle}")

        content = read_text(resolved)
        out_parts: list[str] = []
        next_stack = (*stack, resolved)

        def replace_match(match: re.Match[str]) -> str:
            child = resolve_tex_input(resolved, match.group("target"))
            return expand_file(child, next_stack)

        for line in content.splitlines(keepends=True):
            code, comment = split_comment(line)
            body, line_ending = _split_trailing_line_ending(code)

            full_line_match = FULL_LINE_INCLUDE_RE.fullmatch(body)
            if full_line_match is not None:
                child = resolve_tex_input(resolved, full_line_match.group("target"))
                expanded_child = expand_file(child, next_stack)
                if line_ending and not expanded_child.endswith(("\n", "\r")):
                    expanded_child += line_ending
                out_parts.append(expanded_child + comment)
                continue

            expanded_body = INCLUDE_RE.sub(replace_match, body)
            out_parts.append(expanded_body + line_ending + comment)

        return "".join(out_parts)

    return expand_file(root_path, ())


def extract_graphics_targets(text: str) -> list[str]:
    results: list[str] = []
    for line in text.splitlines(keepends=True):
        code, _comment = split_comment(line)
        body, _ending = _split_trailing_line_ending(code)
        results.extend(match.group("target") for match in GRAPHICS_RE.finditer(body))
    return results
