"""Tests for schedule_compare module."""

from __future__ import annotations

from datetime import datetime

import pytest

from crontab_viz.schedule_compare import compare_schedules, ScheduleCompareResult


FIXED_NOW = datetime(2024, 1, 1, 0, 0)


def test_identical_expressions_have_full_overlap():
    result = compare_schedules("* * * * *", "* * * * *", count=10, now=FIXED_NOW)
    assert len(result.common) == 10
    assert result.only_in_a == []
    assert result.only_in_b == []


def test_overlap_ratio_identical():
    result = compare_schedules("* * * * *", "* * * * *", count=5, now=FIXED_NOW)
    assert result.overlap_ratio == 1.0


def test_disjoint_schedules_no_common():
    # every even minute vs every odd minute — within 10 steps they won't share
    result = compare_schedules("0 * * * *", "30 * * * *", count=5, now=FIXED_NOW)
    assert result.common == []
    assert len(result.only_in_a) > 0
    assert len(result.only_in_b) > 0


def test_overlap_ratio_disjoint():
    result = compare_schedules("0 * * * *", "30 * * * *", count=5, now=FIXED_NOW)
    assert result.overlap_ratio == 0.0


def test_alias_vs_explicit_identical():
    result = compare_schedules("@hourly", "0 * * * *", count=10, now=FIXED_NOW)
    assert len(result.common) == 10
    assert result.only_in_a == []
    assert result.only_in_b == []


def test_summary_contains_expressions():
    result = compare_schedules("* * * * *", "0 * * * *", count=5, now=FIXED_NOW)
    s = result.summary()
    assert "* * * * *" in s
    assert "0 * * * *" in s


def test_summary_contains_overlap_percent():
    result = compare_schedules("* * * * *", "* * * * *", count=5, now=FIXED_NOW)
    assert "100%" in result.summary()


def test_result_dataclass_fields():
    result = compare_schedules("0 9 * * 1", "0 9 * * 5", count=4, now=FIXED_NOW)
    assert isinstance(result, ScheduleCompareResult)
    assert result.expr_a == "0 9 * * 1"
    assert result.expr_b == "0 9 * * 5"


def test_count_respected():
    result = compare_schedules("* * * * *", "0 * * * *", count=60, now=FIXED_NOW)
    total = len(result.common) + len(result.only_in_a) + len(result.only_in_b)
    # both sets have at most 60 items; combined unique can be up to 120
    assert total <= 120


def test_invalid_expression_raises():
    with pytest.raises(Exception):
        compare_schedules("not a cron", "* * * * *", count=5, now=FIXED_NOW)
