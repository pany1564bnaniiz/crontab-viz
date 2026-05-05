"""Tests for crontab_viz.humanize."""

from datetime import datetime, timedelta

import pytest

from crontab_viz.humanize import _delta_to_words, next_run_summary


# ---------------------------------------------------------------------------
# _delta_to_words
# ---------------------------------------------------------------------------

def test_delta_seconds():
    assert _delta_to_words(timedelta(seconds=45)) == "45 seconds"


def test_delta_one_second():
    assert _delta_to_words(timedelta(seconds=1)) == "1 second"


def test_delta_minutes():
    assert _delta_to_words(timedelta(minutes=5)) == "5 minutes"


def test_delta_one_minute():
    assert _delta_to_words(timedelta(minutes=1)) == "1 minute"


def test_delta_hours_only():
    assert _delta_to_words(timedelta(hours=3)) == "3 hours"


def test_delta_hours_and_minutes():
    result = _delta_to_words(timedelta(hours=2, minutes=30))
    assert "2 hours" in result
    assert "30 minutes" in result


def test_delta_days_only():
    assert _delta_to_words(timedelta(days=1)) == "1 day"


def test_delta_days_and_hours():
    result = _delta_to_words(timedelta(days=2, hours=6))
    assert "2 days" in result
    assert "6 hours" in result


# ---------------------------------------------------------------------------
# next_run_summary
# ---------------------------------------------------------------------------

FIXED_NOW = datetime(2024, 1, 15, 12, 0, 0)


def test_summary_contains_header():
    result = next_run_summary("* * * * *", now=FIXED_NOW, count=3)
    assert "Next 3 runs" in result


def test_summary_correct_line_count():
    result = next_run_summary("* * * * *", now=FIXED_NOW, count=3)
    lines = [l for l in result.splitlines() if l.strip()]
    # 1 header + 3 occurrence lines
    assert len(lines) == 4


def test_summary_every_minute_increments():
    result = next_run_summary("* * * * *", now=FIXED_NOW, count=2)
    assert "2024-01-15 12:01" in result
    assert "2024-01-15 12:02" in result


def test_summary_hourly_alias():
    result = next_run_summary("@hourly", now=FIXED_NOW, count=1)
    assert "2024-01-15 13:00" in result


def test_summary_invalid_expression():
    result = next_run_summary("not a cron", now=FIXED_NOW)
    assert "Invalid expression" in result


def test_summary_single_run_grammar():
    result = next_run_summary("* * * * *", now=FIXED_NOW, count=1)
    assert "Next 1 run:" in result


def test_summary_contains_in_phrase():
    result = next_run_summary("* * * * *", now=FIXED_NOW, count=1)
    assert "in" in result
