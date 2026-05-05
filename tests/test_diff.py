"""Tests for crontab_viz.diff."""

import pytest
from crontab_viz.diff import diff, DiffResult


def test_identical_expressions_are_same():
    result = diff("* * * * *", "* * * * *")
    assert result.same is True
    assert result.changed_fields == []


def test_alias_equivalent_to_explicit():
    result = diff("@hourly", "0 * * * *")
    assert result.same is True


def test_different_minute_detected():
    result = diff("0 * * * *", "30 * * * *")
    assert result.same is False
    assert "minute" in result.changed_fields


def test_different_hour_detected():
    result = diff("0 9 * * *", "0 17 * * *")
    assert "hour" in result.changed_fields
    assert "minute" not in result.changed_fields


def test_multiple_changed_fields():
    result = diff("0 9 * * 1", "30 18 * * 5")
    assert "minute" in result.changed_fields
    assert "hour" in result.changed_fields
    assert "dow" in result.changed_fields


def test_summary_same():
    result = diff("* * * * *", "* * * * *")
    assert "equivalent" in result.summary().lower()


def test_summary_different_contains_labels():
    result = diff("0 9 * * *", "0 17 * * *")
    summary = result.summary()
    assert "A:" in summary
    assert "B:" in summary
    assert "hour" in summary


def test_returns_diff_result_type():
    result = diff("5 4 * * *", "5 4 * * *")
    assert isinstance(result, DiffResult)


def test_descriptions_populated():
    result = diff("0 0 * * *", "0 12 * * *")
    assert len(result.description_a) > 0
    assert len(result.description_b) > 0


def test_step_vs_explicit_same_values():
    # 0/2 in minute = every 2 minutes starting at 0; not same as */1
    result = diff("*/2 * * * *", "0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46,48,50,52,54,56,58 * * * *")
    assert result.same is True
