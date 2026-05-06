"""Tests for schedule_compare_cli module."""

from __future__ import annotations

import pytest
from unittest.mock import patch

from crontab_viz.schedule_compare_cli import build_parser, main


def test_build_parser_defaults():
    parser = build_parser()
    args = parser.parse_args(["* * * * *", "0 * * * *"])
    assert args.expr_a == "* * * * *"
    assert args.expr_b == "0 * * * *"
    assert args.count == 20
    assert not args.no_color


def test_build_parser_custom_count():
    parser = build_parser()
    args = parser.parse_args(["-n", "5", "* * * * *", "@hourly"])
    assert args.count == 5


def test_main_runs_without_error(capsys):
    main(["--no-color", "-n", "3", "* * * * *", "* * * * *"])
    captured = capsys.readouterr()
    assert "Schedule Comparison" in captured.out


def test_main_shows_overlap(capsys):
    main(["--no-color", "-n", "5", "* * * * *", "* * * * *"])
    captured = capsys.readouterr()
    assert "Shared" in captured.out


def test_main_invalid_expression_exits(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["--no-color", "bad expr", "* * * * *"])
    assert exc_info.value.code != 0


def test_main_shows_only_in_a(capsys):
    main(["--no-color", "-n", "5", "0 * * * *", "30 * * * *"])
    captured = capsys.readouterr()
    assert "Only in A" in captured.out


def test_main_shows_only_in_b(capsys):
    main(["--no-color", "-n", "5", "0 * * * *", "30 * * * *"])
    captured = capsys.readouterr()
    assert "Only in B" in captured.out
