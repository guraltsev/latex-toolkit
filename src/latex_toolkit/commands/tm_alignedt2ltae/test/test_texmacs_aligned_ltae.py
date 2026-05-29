"""Command transform tests for strict TeXmacs ``aligned`` to ``ltae`` conversion.

The tests call the command's public text transform and assert observable
TeXmacs rewrites. CLI write policy and parser spans are out of scope.
"""

from __future__ import annotations

from unittest import TestCase

import test_support  # noqa: F401

from latex_toolkit.commands.tm_alignedt2ltae.main import transform_text  # noqa: E402


class TexmacsAlignedLtaeTransformTests(TestCase):
    def test_strict_two_column_aligned_t_table_is_rewritten(self) -> None:
        """Strict top-aligned tables become ltae tables with empty cells removed."""

        source = (
            "<\\equation*>\n"
            "  <around|\\||<Em><rsub|\\<psi\\>>|\\|>"
            "<aligned|t|<tformat|<table|"
            "<row|<cell|>|<cell|\\<le\\><around|\\<\\|\\|\\>|f|\\<\\|\\|\\>>>>|"
            "<row|<cell|>|<cell|\\<lesssim\\><rsub|d,\\<alpha\\>,\\<psi\\>>.>>"
            ">>>\n"
            "</equation*>\n"
        )

        converted = transform_text(source)

        self.assertEqual(
            converted,
            "<\\equation*>\n"
            "  <around|\\||<Em><rsub|\\<psi\\>>|\\|>"
            "<ltae|<tformat|<table|"
            "<row|<cell|\\<le\\><around|\\<\\|\\|\\>|f|\\<\\|\\|\\>>>>|"
            "<row|<cell|\\<lesssim\\><rsub|d,\\<alpha\\>,\\<psi\\>>.>>"
            ">>>\n"
            "</equation*>\n",
        )

    def test_nested_strict_aligned_tables_are_rewritten(self) -> None:
        """Nested strict aligned tables are converted inside converted cells."""

        nested = "<aligned|t|<tformat|<table|<row|<cell|>|<cell|inner>>>>>"
        source = f"<aligned|t|<tformat|<table|<row|<cell|>|<cell|outer {nested}>>>>>"

        converted = transform_text(source)

        nested_expected = "<ltae|<tformat|<table|<row|<cell|inner>>>>>"
        self.assertEqual(
            converted,
            f"<ltae|<tformat|<table|<row|<cell|outer {nested_expected}>>>>>",
        )

    def test_first_row_first_cell_prefix_is_hoisted_before_ltae(self) -> None:
        """A leading first-column prefix is moved before the converted table."""

        prefix = "<around|\\<\\|\\|\\>|f|\\<\\|\\|\\>><rsub|X>"
        source = (
            "<aligned|t|<tformat|<table|"
            f"<row|<cell|{prefix}>|<cell|\\<lesssim\\>a>>|"
            "<row|<cell|>|<cell|\\<le\\>b>>"
            ">>>"
        )

        converted = transform_text(source)

        self.assertEqual(
            converted,
            prefix
            + "<ltae|<tformat|<table|"
            "<row|<cell|\\<lesssim\\>a>>|"
            "<row|<cell|\\<le\\>b>>"
            ">>>",
        )

    def test_non_ascii_text_is_preserved_during_rewrite(self) -> None:
        """TeXmacs normalization preserves ordinary Unicode text."""

        unicode_text = "H\u00f6lder \u03b1"
        source = f"<aligned|t|<tformat|<table|<row|<cell|>|<cell|{unicode_text}>>>>>\n"

        converted = transform_text(source)

        self.assertEqual(converted, f"<ltae|<tformat|<table|<row|<cell|{unicode_text}>>>>>\n")

    def test_non_strict_aligned_tables_are_preserved(self) -> None:
        """Aligned tables outside the strict two-column shape remain unchanged."""

        source = (
            "<aligned|c|<tformat|<table|<row|<cell|>|<cell|center>>>>>\n"
            "<aligned|t|<tformat|<table|<row|<cell|x>|<cell|y>>>>>\n"
            "<aligned|t|<tformat|<table|<row|<cell|>|<cell|y>|<cell|z>>>>>\n"
            "<aligned|t|<tformat|<table|<row|<cell|>|<cell|ok>>>>>"
        )

        converted = transform_text(source)

        self.assertEqual(
            converted,
            "<aligned|c|<tformat|<table|<row|<cell|>|<cell|center>>>>>\n"
            "<aligned|t|<tformat|<table|<row|<cell|x>|<cell|y>>>>>\n"
            "<aligned|t|<tformat|<table|<row|<cell|>|<cell|y>|<cell|z>>>>>\n"
            "<ltae|<tformat|<table|<row|<cell|ok>>>>>",
        )
