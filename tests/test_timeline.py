"""Tests for the timeline rendering module."""

from datetime import datetime

import pytest
from crontab_viz.parser import parse
from crontab_viz.timeline import next_occurrences, render_timeline


START = datetime(2024, 1, 15, 10, 0)


def test_next_occurrences_every_minute():
    expr = parse("* * * * *")
    occ = next_occurrences(expr, START, count=5)
    assert len(occ) == 5
    assert occ[0] == datetime(2024, 1, 15, 10, 1)
    assert occ[4] == datetime(2024, 1, 15, 10, 5)


def test_next_occurrences_hourly():
    expr = parse("0 * * * *")
    occ = next_occurrences(expr, START, count=3)
    assert occ[0] == datetime(2024, 1, 15, 11, 0)
    assert occ[1] == datetime(2024, 1, 15, 12, 0)


def test_next_occurrences_daily():
    expr = parse("0 9 * * *")
    occ = next_occurrences(expr, START, count=2)
    assert occ[0] == datetime(2024, 1, 16, 9, 0)
    assert occ[1] == datetime(2024, 1, 17, 9, 0)


def test_next_occurrences_respects_count():
    expr = parse("*/5 * * * *")
    occ = next_occurrences(expr, START, count=4)
    assert len(occ) == 4


def test_render_timeline_contains_header():
    expr = parse("0 12 * * *")
    output = render_timeline(expr, START, count=3)
    assert "0 12 * * *" in output
    assert "2024-01-15 10:00" in output


def test_render_timeline_line_count():
    expr = parse("*/10 * * * *")
    output = render_timeline(expr, START, count=5)
    numbered_lines = [l for l in output.splitlines() if l.strip().startswith(("1.", "2.", "3.", "4.", "5."))]
    assert len(numbered_lines) == 5


def test_render_timeline_relative_time():
    expr = parse("* * * * *")
    output = render_timeline(expr, START, count=1)
    assert "in" in output or "now" in output
