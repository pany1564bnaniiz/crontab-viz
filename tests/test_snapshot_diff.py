"""Tests for crontab_viz.snapshot_diff."""

import pytest

from crontab_viz.snapshot import Snapshot
from crontab_viz.snapshot_diff import diff_snapshots


def _snap(expr="* * * * *", desc="every minute", occurrences=None):
    return Snapshot(
        expression=expr,
        description=desc,
        occurrences=occurrences or ["2024-01-01T00:00:00", "2024-01-01T00:01:00"],
    )


def test_identical_snapshots_no_changes():
    s = _snap()
    result = diff_snapshots(s, s)
    assert not result.has_changes


def test_summary_no_changes():
    s = _snap()
    assert diff_snapshots(s, s).summary() == "No changes between snapshots."


def test_expression_change_detected():
    old = _snap(expr="* * * * *")
    new = _snap(expr="0 * * * *")
    result = diff_snapshots(old, new)
    assert result.expression_changed
    assert result.has_changes


def test_description_change_detected():
    old = _snap(desc="every minute")
    new = _snap(desc="every hour")
    result = diff_snapshots(old, new)
    assert result.description_changed


def test_added_occurrences():
    old = _snap(occurrences=["2024-01-01T00:00:00"])
    new = _snap(occurrences=["2024-01-01T00:00:00", "2024-01-01T00:01:00"])
    result = diff_snapshots(old, new)
    assert "2024-01-01T00:01:00" in result.added
    assert result.removed == []


def test_removed_occurrences():
    old = _snap(occurrences=["2024-01-01T00:00:00", "2024-01-01T00:01:00"])
    new = _snap(occurrences=["2024-01-01T00:00:00"])
    result = diff_snapshots(old, new)
    assert "2024-01-01T00:01:00" in result.removed
    assert result.added == []


def test_summary_includes_expression_change():
    old = _snap(expr="* * * * *")
    new = _snap(expr="0 9 * * *")
    summary = diff_snapshots(old, new).summary()
    assert "* * * * *" in summary
    assert "0 9 * * *" in summary


def test_summary_includes_added_count():
    old = _snap(occurrences=[])
    new = _snap(occurrences=["2024-01-01T00:00:00", "2024-01-01T00:01:00"])
    summary = diff_snapshots(old, new).summary()
    assert "+2" in summary


def test_summary_includes_removed_count():
    old = _snap(occurrences=["2024-01-01T00:00:00", "2024-01-01T00:01:00"])
    new = _snap(occurrences=[])
    summary = diff_snapshots(old, new).summary()
    assert "-2" in summary
