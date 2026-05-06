"""Tests for crontab_viz.calendar_cli."""
from __future__ import annotations

import sys
from io import StringIO
from unittest.mock import patch

import pytest

from crontab_viz.calendar_cli import build_parser, main


def test_build_parser_defaults():
    p = build_parser()
    args = p.parse_args(["0 9 * * *"])
    assert args.expression == "0 9 * * *"
    assert args.year is None
    assert args.month is None
    assert args.no_color is False
    assert args.lookahead == 1500


def test_build_parser_custom_year_month():
    p = build_parser()
    args = p.parse_args(["@daily", "--year", "2025", "--month", "3"])
    assert args.year == 2025
    assert args.month == 3


def test_main_returns_zero_on_valid_expression(capsys):
    result = main(["0 9 * * *", "--year", "2024", "--month", "1", "--no-color"])
    assert result == 0


def test_main_output_contains_month_name(capsys):
    main(["0 9 * * *", "--year", "2024", "--month", "3", "--no-color"])
    captured = capsys.readouterr()
    assert "March" in captured.out


def test_main_output_contains_fire_count(capsys):
    main(["0 9 15 * *", "--year", "2024", "--month", "1", "--no-color"])
    captured = capsys.readouterr()
    assert "1 day" in captured.out


def test_main_invalid_expression_exits_nonzero(capsys):
    result = main(["not a cron", "--year", "2024", "--month", "1"])
    assert result == 1
    captured = capsys.readouterr()
    assert "Error" in captured.err


def test_main_alias_expression(capsys):
    result = main(["@weekly", "--year", "2024", "--month", "1", "--no-color"])
    assert result == 0


def test_main_no_color_flag(capsys):
    result = main(["@daily", "--year", "2024", "--month", "4", "--no-color"])
    captured = capsys.readouterr()
    # With no-color, output should not contain ESC sequences
    assert "\x1b[" not in captured.out
    assert result == 0
