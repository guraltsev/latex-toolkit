"""Tests for observable latex_indent transform behavior at the subprocess boundary.

The tests cover the public ``transform_text`` entrypoint while mocking the
external ``latexindent`` executable. The formatter's internal parsing and exact
output shape for specific TeX inputs are out of scope here.
"""

from __future__ import annotations

from pathlib import Path
from unittest import TestCase
from unittest.mock import patch
import subprocess

from test_support import REPO_ROOT

from latex_toolkit.commands.latex_indent.main import transform_text  # noqa: E402


class LatexIndentTransformTests(TestCase):
    def test_transform_text_uses_only_bundled_settings(self) -> None:
        """The latexindent subprocess uses the bundled settings with line-break rewriting enabled."""

        completed = subprocess.CompletedProcess(
            args=["latexindent"],
            returncode=0,
            stdout="formatted\n",
            stderr="",
        )

        with (
            patch(
                "latex_toolkit.commands.latex_indent.main._find_latexindent_executable",
                return_value="latexindent",
            ),
            patch(
                "latex_toolkit.commands.latex_indent.main.subprocess.run",
                return_value=completed,
            ) as run,
        ):
            result = transform_text("raw\n")

        self.assertEqual(result, "formatted\n")
        self.assertEqual(run.call_count, 1)

        command = run.call_args.args[0]
        self.assertEqual(command[0], "latexindent")
        self.assertEqual(command[1], "-m")
        self.assertEqual(
            command[2],
            f"-l={REPO_ROOT / 'src' / 'latex_toolkit' / 'commands' / 'latex_indent' / 'latexindent.yaml'}",
        )

        self.assertEqual(run.call_args.kwargs["encoding"], "utf-8")

        env = run.call_args.kwargs["env"]
        cwd = run.call_args.kwargs["cwd"]
        for variable in ("HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "XDG_CONFIG_HOME"):
            self.assertEqual(env[variable], cwd)

    def test_transform_text_normalizes_crlf_input_before_running_latexindent(self) -> None:
        """Clipboard-style CRLF input is normalized before formatting and restored after."""

        def fake_run(*args, **kwargs):
            command = args[0]
            staged_input = Path(command[-1]).read_text(encoding="utf-8")
            self.assertEqual(staged_input, "raw\nline\n")
            return subprocess.CompletedProcess(
                args=command,
                returncode=0,
                stdout="\\[\nformatted\nline\n\\]\n",
                stderr="",
            )

        with (
            patch(
                "latex_toolkit.commands.latex_indent.main._find_latexindent_executable",
                return_value="latexindent",
            ),
            patch(
                "latex_toolkit.commands.latex_indent.main.subprocess.run",
                side_effect=fake_run,
            ),
        ):
            result = transform_text("raw\r\nline\r\n")

        self.assertEqual(result, "\\[\r\nformatted\r\nline\r\n\\]\r\n")

    def test_transform_text_preserves_latexindent_output_shape(self) -> None:
        """The wrapper preserves latexindent output instead of applying extra Python formatting."""

        completed = subprocess.CompletedProcess(
            args=["latexindent"],
            returncode=0,
            stdout=(
                "\\begin{remark}\n"
                "This is a wrapped\n"
                "plain-text paragraph.\n"
                "\n"
                "\n"
                "\\begin{equation}\n"
                "a + \\begin{aligned}[t] b &= c \\\\\n"
                "               d     &= e\\end{aligned}\n"
                "\\end{equation}\n"
            ),
            stderr="",
        )

        with (
            patch(
                "latex_toolkit.commands.latex_indent.main._find_latexindent_executable",
                return_value="latexindent",
            ),
            patch(
                "latex_toolkit.commands.latex_indent.main.subprocess.run",
                return_value=completed,
            ),
        ):
            result = transform_text("raw\n")

        self.assertEqual(
            result,
            (
                "\\begin{remark}\n"
                "This is a wrapped\n"
                "plain-text paragraph.\n"
                "\n"
                "\n"
                "\\begin{equation}\n"
                "a + \\begin{aligned}[t] b &= c \\\\\n"
                "               d     &= e\\end{aligned}\n"
                "\\end{equation}\n"
            ),
        )
