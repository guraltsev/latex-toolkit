r"""Protect the command scripts in ``src`` that launchers start with any Python.

The tests run each real ``src/<command>.py`` script in a child process with the
interpreter running the tests, from a working folder outside the repository and
without ``PYTHONPATH``. Nothing is mocked. Whether a given interpreter has the
dependencies installed is out of scope.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

SOURCE_ROOT = Path(__file__).parents[1] / "src"

COMMAND_SCRIPTS = [
    "lt_brace_args",
    "lt_eqnum_label",
    "lt_full_normalize",
    "lt_greek_latex2unicode",
    "lt_greek_unicode2latex",
    "lt_math_dollar2latex",
    "lt_math_latex2dollar",
    "lt_sentence_per_line",
    "lt_syntax_regularizer",
    "lt_template",
    "mdt_brace_args",
    "mdt_full_normalize",
    "mdt_greek_latex2unicode",
    "mdt_greek_unicode2latex",
    "mdt_math_dollar2latex",
    "mdt_math_latex2dollar",
    "mdt_sentence_per_line",
    "mdt_syntax_regularizer",
]


def _run_script(name: str, arguments: list[str], working_folder: Path) -> subprocess.CompletedProcess[str]:
    """Run one command script from ``working_folder`` without ``PYTHONPATH``."""
    environment = {key: value for key, value in os.environ.items() if key != "PYTHONPATH"}
    return subprocess.run(
        [sys.executable, str(SOURCE_ROOT / f"{name}.py"), *arguments],
        capture_output=True,
        check=False,
        cwd=working_folder,
        encoding="utf-8",
        env=environment,
    )


@pytest.mark.parametrize("name", [pytest.param(name, id=name) for name in COMMAND_SCRIPTS])
def test_each_command_script_starts_its_command_from_any_folder(name: str, tmp_path: Path) -> None:
    """Each command script runs its command when started from an unrelated folder."""
    completed = _run_script(name, ["--help"], tmp_path)

    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.startswith("usage:")


def test_a_command_script_resolves_relative_paths_against_the_callers_folder(tmp_path: Path) -> None:
    """A relative input and output path name files in the caller's working folder."""
    (tmp_path / "main.tex").write_text("  First sentence. Second sentence.", encoding="utf-8")

    completed = _run_script("lt_full_normalize", ["main.tex", "-o", "out.tex"], tmp_path)

    assert completed.returncode == 0, completed.stderr
    assert (tmp_path / "out.tex").read_text(encoding="utf-8") == "First sentence.\nSecond sentence."
    assert (tmp_path / "main.tex").read_text(encoding="utf-8") == "  First sentence. Second sentence."
