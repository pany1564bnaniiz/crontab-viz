"""Tests for the crontab expression parser."""

import pytest
from crontab_viz.parser import parse, ParseError


def test_wildcard_minute():
    expr = parse("* * * * *")
    assert expr.minute == list(range(0, 60))


def test_specific_values():
    expr = parse("30 14 1 6 *")
    assert expr.minute == [30]
    assert expr.hour == [14]
    assert expr.day_of_month == [1]
    assert expr.month == [6]
    assert expr.day_of_week == list(range(0, 7))


def test_step_expression():
    expr = parse("*/15 * * * *")
    assert expr.minute == [0, 15, 30, 45]


def test_range_expression():
    expr = parse("0 9-17 * * *")
    assert expr.hour == list(range(9, 18))


def test_comma_list():
    expr = parse("0 8,12,18 * * *")
    assert expr.hour == [8, 12, 18]


def test_month_alias():
    expr = parse("0 0 1 Jan *")
    assert expr.month == [1]


def test_dow_alias():
    expr = parse("0 0 * * Mon")
    assert expr.day_of_week == [1]


def test_raw_preserved():
    raw = "5 4 * * sun"
    expr = parse(raw)
    assert expr.raw == raw


def test_invalid_field_count():
    with pytest.raises(ParseError, match="Expected 5 fields"):
        parse("* * * *")


def test_invalid_value():
    with pytest.raises(ParseError):
        parse("abc * * * *")


def test_step_with_range():
    expr = parse("0-30/10 * * * *")
    assert expr.minute == [0, 10, 20, 30]
