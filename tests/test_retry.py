"""Tests for crontab_viz.retry."""
from __future__ import annotations

from datetime import datetime

import pytest

from crontab_viz.retry import analyze_retry, RetryAnalysis, RetryConflict


FIXED_NOW = datetime(2024, 1, 15, 12, 0, 0)


def test_returns_retry_analysis():
    result = analyze_retry("* * * * *", now=FIXED_NOW)
    assert isinstance(result, RetryAnalysis)


def test_invalid_expression_sets_error():
    result = analyze_retry("invalid", now=FIXED_NOW)
    assert not result.ok
    assert result.error is not None


def test_invalid_interval_sets_error():
    result = analyze_retry("* * * * *", retry_interval_minutes=0, now=FIXED_NOW)
    assert not result.ok
    assert "retry_interval_minutes" in result.error


def test_invalid_max_retries_sets_error():
    result = analyze_retry("* * * * *", max_retries=0, now=FIXED_NOW)
    assert not result.ok
    assert "max_retries" in result.error


def test_every_minute_with_1min_interval_has_conflicts():
    # Every minute schedule + 1-minute retry interval → every retry lands on a run
    result = analyze_retry("* * * * *", retry_interval_minutes=1, max_retries=2, now=FIXED_NOW)
    assert result.ok
    assert result.has_conflicts


def test_every_minute_conflict_type():
    result = analyze_retry("* * * * *", retry_interval_minutes=1, max_retries=1, now=FIXED_NOW)
    assert all(isinstance(c, RetryConflict) for c in result.conflicts)


def test_daily_schedule_no_conflict_with_short_retry():
    # Runs once a day; 5-minute retries won't hit next day's run
    result = analyze_retry("0 9 * * *", retry_interval_minutes=5, max_retries=3,
                           window=5, now=FIXED_NOW)
    assert result.ok
    assert not result.has_conflicts


def test_hourly_schedule_conflict_when_retry_equals_interval():
    # Hourly schedule + 60-minute retry → retry lands exactly on next run
    result = analyze_retry("0 * * * *", retry_interval_minutes=60, max_retries=1,
                           window=10, now=FIXED_NOW)
    assert result.ok
    assert result.has_conflicts


def test_conflict_str_contains_times():
    result = analyze_retry("* * * * *", retry_interval_minutes=1, max_retries=1, now=FIXED_NOW)
    assert result.has_conflicts
    s = str(result.conflicts[0])
    assert "Retry #" in s
    assert "overlaps" in s


def test_summary_no_conflicts():
    result = analyze_retry("0 9 * * *", retry_interval_minutes=5, max_retries=3,
                           window=3, now=FIXED_NOW)
    summary = result.summary()
    assert "No retry conflicts" in summary


def test_summary_with_conflicts():
    result = analyze_retry("* * * * *", retry_interval_minutes=1, max_retries=1, now=FIXED_NOW)
    summary = result.summary()
    assert "conflict" in summary.lower()


def test_summary_error():
    result = analyze_retry("bad expr", now=FIXED_NOW)
    assert "Error" in result.summary()


def test_expression_stored():
    expr = "30 6 * * 1"
    result = analyze_retry(expr, now=FIXED_NOW)
    assert result.expression == expr


def test_retry_params_stored():
    result = analyze_retry("* * * * *", retry_interval_minutes=10, max_retries=4, now=FIXED_NOW)
    assert result.retry_interval_minutes == 10
    assert result.max_retries == 4
