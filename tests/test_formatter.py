"""Tests for crontab_viz.formatter."""

import pytest
from crontab_viz.parser import parse
from crontab_viz.formatter import describe, _ordinal


def test_ordinal_basic():
    assert _ordinal(1) == "1st"
    assert _ordinal(2) == "2nd"
    assert _ordinal(3) == "3rd"
    assert _ordinal(4) == "4th"
    assert _ordinal(11) == "11th"
    assert _ordinal(12) == "12th"
    assert _ordinal(13) == "13th"
    assert _ordinal(21) == "21st"


def test_describe_every_minute():
    expr = parse("* * * * *")
    result = describe(expr)
    assert "every minute" in result


def test_describe_hourly():
    expr = parse("0 * * * *")
    result = describe(expr)
    assert "0" in result


def test_describe_daily():
    expr = parse("30 6 * * *")
    result = describe(expr)
    assert "30" in result
    assert "6" in result


def test_describe_specific_weekdays():
    expr = parse("0 9 * * 1,5")
    result = describe(expr)
    assert "Monday" in result
    assert "Friday" in result


def test_describe_specific_months():
    expr = parse("0 0 1 3,6 *")
    result = describe(expr)
    assert "March" in result
    assert "June" in result


def test_describe_specific_day_of_month():
    expr = parse("0 0 15 * *")
    result = describe(expr)
    assert "15th" in result


def test_describe_alias_daily():
    expr = parse("@daily")
    result = describe(expr)
    assert isinstance(result, str)
    assert len(result) > 0
