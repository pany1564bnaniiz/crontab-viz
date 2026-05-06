"""Tests for crontab_viz.next_n and crontab_viz.next_n_cli."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import patch
import pytest

from crontab_viz.next_n import compute, format_next_n, compare_next_n, NextNResult


NOW = datetime(2024, 1, 15, 12, 0, 0)


# ---------------------------------------------------------------------------
# compute()
# ---------------------------------------------------------------------------

def test_compute_returns_correct_count():
    result = compute("* * * * *", count=3, now=NOW)
    assert result.ok
    assert len(result.occurrences) == 3


def test_compute_default_count_is_five():
    result = compute("0 * * * *", now=NOW)
    assert result.ok
    assert len(result.occurrences) == 5


def test_compute_invalid_expression_sets_error():
    result = compute("not-a-cron", now=NOW)
    assert not result.ok
    assert result.error is not None
    assert result.occurrences == []


def test_compute_count_too_small_is_error():
    result = compute("* * * * *", count=0, now=NOW)
    assert not result.ok


def test_compute_count_too_large_is_error():
    result = compute("* * * * *", count=101, now=NOW)
    assert not result.ok


def test_compute_alias_at_hourly():
    result = compute("@hourly", count=2, now=NOW)
    assert result.ok
    assert len(result.occurrences) == 2


def test_compute_occurrences_are_in_future():
    result = compute("* * * * *", count=5, now=NOW)
    for dt in result.occurrences:
        assert dt > NOW


def test_compute_occurrences_are_ordered():
    result = compute("*/15 * * * *", count=4, now=NOW)
    assert result.occurrences == sorted(result.occurrences)


# ---------------------------------------------------------------------------
# format_next_n()
# ---------------------------------------------------------------------------

def test_format_next_n_contains_expression():
    result = compute("0 9 * * 1", count=2, now=NOW)
    text = format_next_n(result, now=NOW)
    assert "0 9 * * 1" in text


def test_format_next_n_shows_count_lines():
    result = compute("0 * * * *", count=3, now=NOW)
    text = format_next_n(result, now=NOW)
    # Numbered lines 1. 2. 3.
    assert "  1." in text
    assert "  3." in text


def test_format_next_n_error_result():
    result = NextNResult(expression="bad", error="parse failed")
    text = format_next_n(result)
    assert "Error" in text
    assert "parse failed" in text


# ---------------------------------------------------------------------------
# compare_next_n()
# ---------------------------------------------------------------------------

def test_compare_next_n_multiple_expressions():
    exprs = ["* * * * *", "0 * * * *"]
    results = compare_next_n(exprs, count=2, now=NOW)
    assert len(results) == 2
    assert all(r.ok for r in results)


def test_compare_next_n_mixed_valid_invalid():
    exprs = ["* * * * *", "bad-expr"]
    results = compare_next_n(exprs, count=2, now=NOW)
    assert results[0].ok
    assert not results[1].ok
