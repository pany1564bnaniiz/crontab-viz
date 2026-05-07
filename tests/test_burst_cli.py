"""Tests for crontab_viz.burst_cli."""

from __future__ import annotations

import io
from unittest.mock import patch

import pytest

from crontab_viz.burst_cli import build_parser, main


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def test_build_parser_returns_parser():
    import argparse
    assert isinstance(build_parser(), argparse.ArgumentParser)


def test_build_parser_defaults():
    p = build_parser()
    args = p.parse_args(["* * * * *"])
    assert args.window == 3600
    assert args.threshold == 10
    assert args.lookahead == 500
    assert args.top == 5


def test_build_parser_custom_values():
    p = build_parser()
    args = p.parse_args(["0 * * * *", "--window", "600", "--threshold", "3"])
    assert args.window == 600
    assert args.threshold == 3


# ---------------------------------------------------------------------------
# main()
# ---------------------------------------------------------------------------

def test_main_returns_zero_on_valid():
    code = main(["0 9 * * *", "--threshold", "5"])
    assert code == 0


def test_main_returns_one_on_invalid():
    code = main(["not valid at all"])
    assert code == 1


def test_main_output_contains_expression(capsys):
    main(["* * * * *"])
    captured = capsys.readouterr()
    assert "* * * * *" in captured.out


def test_main_no_burst_message(capsys):
    main(["0 9 * * *", "--window", "3600", "--threshold", "5"])
    captured = capsys.readouterr()
    assert "No burst" in captured.out


def test_main_burst_detected_message(capsys):
    main(["* * * * *", "--window", "3600", "--threshold", "10"])
    captured = capsys.readouterr()
    assert "fires" in captured.out


def test_main_top_limits_output(capsys):
    """--top 1 should show at most 1 burst window line."""
    main(["* * * * *", "--top", "1", "--threshold", "5"])
    captured = capsys.readouterr()
    lines = [l for l in captured.out.splitlines() if "fires" in l and l.startswith("  ")]
    assert len(lines) <= 1
