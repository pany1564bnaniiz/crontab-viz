"""Tests for crontab_viz.retry_cli."""
from __future__ import annotations

import pytest
from unittest.mock import patch

from crontab_viz.retry_cli import build_parser, main


def test_build_parser_returns_parser():
    p = build_parser()
    assert p is not None


def test_build_parser_defaults():
    p = build_parser()
    args = p.parse_args(["* * * * *"])
    assert args.interval == 5
    assert args.retries == 3
    assert args.window == 24
    assert not args.no_color


def test_build_parser_custom_values():
    p = build_parser()
    args = p.parse_args(["0 * * * *", "-i", "10", "-r", "5", "-w", "48"])
    assert args.interval == 10
    assert args.retries == 5
    assert args.window == 48


def test_main_returns_zero_on_valid(capsys):
    rc = main(["0 9 * * *", "--no-color"])
    assert rc == 0


def test_main_returns_one_on_invalid(capsys):
    rc = main(["not a cron", "--no-color"])
    assert rc == 1


def test_main_no_conflict_output(capsys):
    main(["0 9 * * *", "--no-color", "-w", "3"])
    out = capsys.readouterr().out
    assert "No conflicts" in out


def test_main_conflict_output(capsys):
    # Every-minute schedule with 1-minute retry should show conflicts
    main(["* * * * *", "--no-color", "-i", "1", "-r", "1"])
    out = capsys.readouterr().out
    assert "conflict" in out.lower() or "Retry" in out


def test_main_invalid_expression_stderr(capsys):
    main(["bad", "--no-color"])
    err = capsys.readouterr().err
    assert "Error" in err
