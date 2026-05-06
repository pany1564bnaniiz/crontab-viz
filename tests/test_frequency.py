"""Tests for crontab_viz.frequency."""

import pytest

from crontab_viz.frequency import (
    FrequencyStats,
    _fmt_interval,
    _label,
    compute_frequency,
    compare_frequencies,
)
from crontab_viz.parser import ParseError


# ---------------------------------------------------------------------------
# _fmt_interval
# ---------------------------------------------------------------------------

def test_fmt_interval_seconds():
    assert _fmt_interval(30) == "30s"


def test_fmt_interval_minutes():
    result = _fmt_interval(90)
    assert result.endswith("m")


def test_fmt_interval_hours():
    result = _fmt_interval(7200)
    assert result == "2.0h"


def test_fmt_interval_days():
    result = _fmt_interval(172800)
    assert result == "2.0d"


# ---------------------------------------------------------------------------
# _label
# ---------------------------------------------------------------------------

def test_label_every_minute():
    assert _label(1440) == "every-minute"


def test_label_high_frequency():
    assert _label(48) == "high-frequency"


def test_label_daily():
    assert _label(1) == "daily"


def test_label_weekly():
    assert _label(1 / 7) == "weekly"


def test_label_low_frequency():
    assert _label(0.01) == "low-frequency"


# ---------------------------------------------------------------------------
# compute_frequency
# ---------------------------------------------------------------------------

def test_compute_frequency_every_minute():
    stats = compute_frequency("* * * * *")
    assert isinstance(stats, FrequencyStats)
    assert stats.label == "every-minute"
    assert abs(stats.runs_per_hour - 60) < 1


def test_compute_frequency_hourly():
    stats = compute_frequency("0 * * * *")
    assert stats.label == "high-frequency"
    assert abs(stats.runs_per_day - 24) < 1


def test_compute_frequency_daily():
    stats = compute_frequency("0 9 * * *")
    assert stats.label == "daily"
    assert abs(stats.runs_per_day - 1) < 0.1


def test_compute_frequency_alias():
    stats = compute_frequency("@hourly")
    assert abs(stats.runs_per_day - 24) < 1


def test_compute_frequency_invalid_raises():
    with pytest.raises(ParseError):
        compute_frequency("not a cron")


def test_compute_frequency_str_repr():
    stats = compute_frequency("* * * * *")
    text = str(stats)
    assert "every-minute" in text
    assert "/day" in text


# ---------------------------------------------------------------------------
# compare_frequencies
# ---------------------------------------------------------------------------

def test_compare_frequencies_order():
    results = compare_frequencies(["0 9 * * *", "* * * * *", "0 * * * *"])
    labels = [r.label for r in results]
    assert labels[0] == "every-minute"
    assert labels[-1] == "daily"


def test_compare_frequencies_returns_all():
    exprs = ["0 9 * * *", "0 * * * *"]
    results = compare_frequencies(exprs)
    assert len(results) == len(exprs)
