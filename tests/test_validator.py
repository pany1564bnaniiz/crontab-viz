"""Tests for crontab_viz.validator."""

import pytest
from crontab_viz.validator import validate, ValidationResult


def test_valid_every_minute():
    result = validate("* * * * *")
    assert result.valid
    assert result.errors == []


def test_valid_alias_hourly():
    result = validate("@hourly")
    assert result.valid
    assert result.errors == []


def test_valid_specific_schedule():
    result = validate("30 8 * * 1-5")
    assert result.valid


def test_invalid_too_few_fields():
    result = validate("* * * *")
    assert not result.valid
    assert any("5 fields" in e for e in result.errors)


def test_invalid_too_many_fields():
    result = validate("* * * * * *")
    assert not result.valid
    assert any("5 fields" in e for e in result.errors)


def test_invalid_minute_out_of_range():
    result = validate("60 * * * *")
    assert not result.valid
    assert any("minute" in e for e in result.errors)


def test_invalid_hour_out_of_range():
    result = validate("0 25 * * *")
    assert not result.valid
    assert any("hour" in e for e in result.errors)


def test_invalid_dom_out_of_range():
    result = validate("0 0 32 * *")
    assert not result.valid
    assert any("day-of-month" in e for e in result.errors)


def test_invalid_month_out_of_range():
    result = validate("0 0 1 13 *")
    assert not result.valid
    assert any("month" in e for e in result.errors)


def test_invalid_dow_out_of_range():
    result = validate("0 0 * * 8")
    assert not result.valid
    assert any("day-of-week" in e for e in result.errors)


def test_warning_dom_and_dow_both_restricted():
    result = validate("0 9 15 * 1")
    assert result.valid
    assert len(result.warnings) == 1
    assert "union" in result.warnings[0]


def test_no_warning_when_only_dom_restricted():
    result = validate("0 9 15 * *")
    assert result.valid
    assert result.warnings == []


def test_bool_coercion_valid():
    assert bool(validate("* * * * *")) is True


def test_bool_coercion_invalid():
    assert bool(validate("99 * * * *")) is False


def test_unknown_alias():
    result = validate("@unknown")
    assert not result.valid
