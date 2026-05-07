"""Tests for crontab_viz.burst."""

from __future__ import annotations

from datetime import datetime

import pytest

from crontab_viz.burst import detect_bursts, BurstResult, BurstWindow


FIXED = datetime(2024, 1, 15, 0, 0, 0)


# ---------------------------------------------------------------------------
# detect_bursts – happy paths
# ---------------------------------------------------------------------------

def test_returns_burst_result():
    result = detect_bursts("* * * * *", since=FIXED)
    assert isinstance(result, BurstResult)


def test_every_minute_produces_bursts():
    """Every-minute schedule fires 60 times per hour — well above default threshold."""
    result = detect_bursts("* * * * *", window_seconds=3600, threshold=10, since=FIXED)
    assert result.ok()
    assert len(result.bursts) > 0


def test_burst_window_type():
    result = detect_bursts("* * * * *", since=FIXED)
    assert all(isinstance(b, BurstWindow) for b in result.bursts)


def test_burst_count_matches_occurrences_length():
    result = detect_bursts("* * * * *", window_seconds=600, threshold=5, since=FIXED)
    for bw in result.bursts:
        assert bw.count == len(bw.occurrences)


def test_daily_schedule_no_burst():
    """Daily schedule fires once per day — cannot burst within an hour."""
    result = detect_bursts(
        "0 9 * * *", window_seconds=3600, threshold=5, since=FIXED
    )
    assert result.ok()
    assert result.bursts == []


def test_no_burst_summary_message():
    result = detect_bursts("0 9 * * *", window_seconds=3600, threshold=5, since=FIXED)
    assert "No burst" in result.summary()


def test_burst_summary_message():
    result = detect_bursts("* * * * *", window_seconds=3600, threshold=10, since=FIXED)
    assert "burst window" in result.summary()


def test_threshold_respected():
    """Raising threshold high enough should suppress bursts."""
    result = detect_bursts(
        "* * * * *", window_seconds=60, threshold=100, since=FIXED
    )
    # At most 1 fire per minute, so 100 in 60 s is impossible.
    assert result.bursts == []


def test_window_seconds_stored():
    result = detect_bursts("* * * * *", window_seconds=1800, since=FIXED)
    assert result.window_seconds == 1800


def test_threshold_stored():
    result = detect_bursts("* * * * *", threshold=7, since=FIXED)
    assert result.threshold == 7


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

def test_invalid_expression_sets_error():
    result = detect_bursts("not a cron", since=FIXED)
    assert not result.ok()
    assert result.error is not None


def test_invalid_expression_empty_bursts():
    result = detect_bursts("99 99 99 99 99", since=FIXED)
    assert result.bursts == []


def test_error_summary_contains_error():
    result = detect_bursts("bad", since=FIXED)
    assert "Error" in result.summary()


# ---------------------------------------------------------------------------
# BurstWindow helpers
# ---------------------------------------------------------------------------

def test_burst_window_duration():
    start = datetime(2024, 1, 15, 10, 0)
    end = datetime(2024, 1, 15, 10, 30)
    bw = BurstWindow(start=start, end=end, count=5)
    assert bw.duration_seconds() == 1800.0
