#!/usr/bin/env python3
"""
Reformat LaTeX math environments according to strict rules:

- Remove all indentation.
- Separate + - * operators with a single space.
- Align & characters with a single space, except at line start (no space before, one after).
- Put \\ on its own line, except inside \substack.
- Remove source line breaks unless a comment % is present, or the resulting line
  exceeds 100 characters.  In that case split at top‑level relation symbols first,
  then + - *, falling back to lower nesting levels if necessary.

Uses pylatexenc to parse and re‑emit the LaTeX.
"""

import sys
import re
from pylatexenc.latexwalker import (
    LatexWalker,
    LatexEnvironmentNode,
    LatexMacroNode,
    LatexGroupNode,
    LatexCommentNode,
    LatexCharsNode,
    LatexNodesRenderer
)

# ── Which environments to process ──────────────────────────────────────────
MATH_ENVIRONMENTS = {
    'align', 'align*',
    'alignat', 'alignat*',
    'equation', 'equation*',
    'gather', 'gather*',
    'multline', 'multline*',
    'flalign', 'flalign*',
    'math', 'displaymath'
}

# ── Priority lists for line splitting ──────────────────────────────────────
RELATION_SYMBOLS = [
    r'\eqdef', r'\eqd', r'\leq', r'\lesssim', r'\approx', r'\eqsim',
    r'\geq', r'\geqslant', r'\leqslant', r'\le', r'\ge',
    '=', '<', '>', r'\ll', r'\gg', r'\simeq', r'\cong', r'\sim'
]
OPERATOR_SYMBOLS = ['+', '-', '*']

# ── Helper: compute brace depth at each character ──────────────────────────
def get_depth_array(s):
    """Return a list of depth values for each character in s."""
    depth = []
    cur = 0
    for ch in s:
        if ch == '{':
            depth.append(cur)
            cur += 1
        elif ch == '}':
            cur -= 1
            depth.append(cur)
        else:
            depth.append(cur)
    return depth

def find_split_index(line, max_len, symbols, allowed_depth):
    """Return the largest index <= max_len where a symbol in `symbols` starts
    and the brace depth is <= allowed_depth, or -1 if none."""
    depth_arr = get_depth_array(line)
    best = -1
    for sym in symbols:
        start = 0
        while True:
            idx = line.find(sym, start)
            if idx == -1:
                break
            # skip if inside a longer command name (e.g. \leq inside \nleq)
            if sym.startswith('\\') and idx > 0 and line[idx-1].isalpha():
                start = idx + 1
                continue
            if idx < len(depth_arr) and depth_arr[idx] <= allowed_depth:
                if idx <= max_len:
                    best = max(best, idx)
            start = idx + 1
    return best

def split_long_line(line, max_len=100):
    """Split a long line at the best spot.  Return a list of lines."""
    if len(line) <= max_len:
        return [line]

    # Try increasing depths until we find a suitable break
    for allowed_depth in range(5):
        # relation symbols first
        idx = find_split_index(line, max_len, RELATION_SYMBOLS, allowed_depth)
        if idx != -1:
            left = line[:idx]
            right = line[idx:]
            return [left] + split_long_line(right, max_len)

        # then operators
        idx = find_split_index(line, max_len, OPERATOR_SYMBOLS, allowed_depth)
        if idx != -1:
            left = line[:idx]
            right = line[idx:]
            return [left] + split_long_line(right, max_len)

    # fallback: split at last space before max_len
    last_space = line.rfind(' ', 0, max_len)
    if last_space != -1:
        return [line[:last_space]] + split_long_line(line[last_space+1:], max_len)

    # hard break at max_len
    return [line[:max_len]] + split_long_line(line[max_len:], max_len)


# ── Formatting the body of a math environment ──────────────────────────────
def render_nodes_to_formatted_string(nodes, substack=False, start_of_line=True):
    """
    Walk a list of pylatexenc nodes and return a string with the desired
    whitespace rules applied.
    """
    result = []
    last_char_was_space = False
    # state variables (modified by append)
    sl = [start_of_line]         # list so we can mutate inside append

    def append(s):
        nonlocal last_char_was_space
        if not s:
            return
        result.append(s)
        if s.endswith(' ') or s.endswith('\n') or s.endswith('\t'):
            last_char_was_space = True
        else:
            last_char_was_space = False
        if s.endswith('\n'):
            sl[0] = True
        else:
            sl[0] = False

    for node in nodes:
        if isinstance(node, LatexCharsNode):
            text = node.chars
            i = 0
            while i < len(text):
                ch = text[i]
                if ch == '&':
                    if sl[0]:
                        # no space before, one after
                        append('& ')
                    else:
                        if not last_char_was_space:
                            append(' ')
                        append('& ')
                    last_char_was_space = True
                    sl[0] = False
                elif ch in ('+', '-', '*'):
                    if not last_char_was_space:
                        append(' ')
                    append(ch)
                    append(' ')
                    last_char_was_space = True
                    sl[0] = False
                elif ch == '\n':
                    # source newline – ignore (we will only insert our own)
                    pass
                else:
                    if sl[0] and ch == ' ':
                        # strip leading spaces (indentation)
                        pass
                    else:
                        append(ch)
                    sl[0] = False
                i += 1

        elif isinstance(node, LatexCommentNode):
            # keep comment and its terminating newline
            append(node.comment)          # includes '%'
            append('\n')
            sl[0] = True
            last_char_was_space = False

        elif isinstance(node, LatexMacroNode):
            macroname = node.macroname
            star_str = '*' if getattr(node, 'star', None) == '*' else ''

            if macroname == 'substack':
                append(r'\substack{')
                arg_group = node.nodeargs[0]
                inner = render_nodes_to_formatted_string(
                    arg_group.nodelist, substack=True, start_of_line=False
                )
                append(inner)
                append('}')
                sl[0] = False
                last_char_was_space = False

            elif macroname == '\\':          # \\ or \\*
                macro_str = r'\\' + star_str
                if substack:
                    append(macro_str)
                else:
                    if not sl[0]:
                        append('\n')
                    append(macro_str)
                    append('\n')
                    sl[0] = True
                    last_char_was_space = False

            else:
                # ordinary macro – reconstruct manually to format arguments
                append('\\' + macroname + star_str)
                for arg in node.nodeargs:
                    if arg.delimiters[0] == '[':
                        append('[')
                        inner = render_nodes_to_formatted_string(
                            arg.nodelist, substack, start_of_line=False
                        )
                        append(inner)
                        append(']')
                    else:
                        append('{')
                        inner = render_nodes_to_formatted_string(
                            arg.nodelist, substack, start_of_line=False
                        )
                        append(inner)
                        append('}')
                sl[0] = False
                last_char_was_space = False

        elif isinstance(node, LatexGroupNode):
            append('{')
            inner = render_nodes_to_formatted_string(
                node.nodelist, substack, start_of_line=False
            )
            append(inner)
            append('}')
            sl[0] = False
            last_char_was_space = False

        elif isinstance(node, LatexEnvironmentNode):
            # nested environment – leave untouched
            verb = node.latex_verbatim()
            append(verb)
            if verb.endswith('\n'):
                sl[0] = True
            else:
                sl[0] = False
            last_char_was_space = False

        else:
            # any other node (math mode, etc.)
            verb = node.latex_verbatim()
            append(verb)
            if verb.endswith('\n'):
                sl[0] = True
            else:
                sl[0] = False
            last_char_was_space = False

    return ''.join(result)


# ── Tree traversal to find and replace math environments ───────────────────
def process_tree(nodes):
    """Recursively walk the node tree and reformat math environments."""
    for node in nodes:
        if isinstance(node, LatexEnvironmentNode) and node.envname in MATH_ENVIRONMENTS:
            if not node.nodelist:
                continue
            # 1. render with spacing rules
            formatted = render_nodes_to_formatted_string(
                node.nodelist, substack=False, start_of_line=True
            )
            # 2. handle long lines
            lines = formatted.split('\n')
            final_lines = []
            for line in lines:
                if len(line) > 100:
                    final_lines.extend(split_long_line(line))
                else:
                    final_lines.append(line)
            final_str = '\n'.join(final_lines)
            # 3. replace the body with a single text node
            node.nodelist = [LatexCharsNode(chars=final_str, pos=0, len=0)]
        else:
            # recurse into node children
            if hasattr(node, 'nodelist') and node.nodelist is not None:
                process_tree(node.nodelist)
            if hasattr(node, 'nodeargs') and node.nodeargs:
                for arg in node.nodeargs:
                    process_tree(arg.nodelist)


# ── Main ───────────────────────────────────────────────────────────────────
def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='Reformat math environments with pylatexenc'
    )
    parser.add_argument('input', help='Input .tex file')
    parser.add_argument('output', help='Output .tex file')
    args = parser.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        latex_source = f.read()

    walker = LatexWalker(latex_source)
    nodelist, pos, length = walker.get_latex_nodes(0)

    process_tree(nodelist)

    renderer = LatexNodesRenderer()
    result = renderer.render(nodelist)

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(result)

if __name__ == '__main__':
    main()