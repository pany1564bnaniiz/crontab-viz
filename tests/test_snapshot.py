"""Tests for crontab_viz.snapshot."""

import json
import os

import pytest

from crontab_viz.snapshot import (
    Snapshot,
    clear_snapshots,
    find_by_label,
    load_snapshots,
    take_snapshot,
)


@pytest.fixture()
def snap_file(tmp_path):
    return str(tmp_path / "snaps.json")


def _make_snap(expr="* * * * *", desc="every minute", label=None):
    return Snapshot(
        expression=expr,
        description=desc,
        occurrences=["2024-01-01T00:00:00", "2024-01-01T00:01:00"],
        label=label,
    )


def test_take_snapshot_creates_file(snap_file):
    take_snapshot(_make_snap(), path=snap_file)
    assert os.path.exists(snap_file)


def test_take_snapshot_stores_expression(snap_file):
    take_snapshot(_make_snap(expr="0 9 * * 1"), path=snap_file)
    snaps = load_snapshots(snap_file)
    assert snaps[0].expression == "0 9 * * 1"


def test_load_snapshots_empty(snap_file):
    assert load_snapshots(snap_file) == []


def test_multiple_snapshots_accumulate(snap_file):
    take_snapshot(_make_snap(expr="* * * * *"), path=snap_file)
    take_snapshot(_make_snap(expr="0 * * * *"), path=snap_file)
    snaps = load_snapshots(snap_file)
    assert len(snaps) == 2


def test_clear_snapshots(snap_file):
    take_snapshot(_make_snap(), path=snap_file)
    clear_snapshots(snap_file)
    assert load_snapshots(snap_file) == []


def test_snapshot_label_stored(snap_file):
    take_snapshot(_make_snap(label="prod"), path=snap_file)
    snaps = load_snapshots(snap_file)
    assert snaps[0].label == "prod"


def test_find_by_label_returns_latest(snap_file):
    take_snapshot(_make_snap(expr="* * * * *", label="nightly"), path=snap_file)
    take_snapshot(_make_snap(expr="0 2 * * *", label="nightly"), path=snap_file)
    result = find_by_label("nightly", path=snap_file)
    assert result is not None
    assert result.expression == "0 2 * * *"


def test_find_by_label_missing_returns_none(snap_file):
    assert find_by_label("ghost", path=snap_file) is None


def test_snapshot_round_trip(snap_file):
    snap = _make_snap(expr="30 6 * * 1-5", desc="weekday mornings", label="work")
    take_snapshot(snap, path=snap_file)
    loaded = load_snapshots(snap_file)[0]
    assert loaded.expression == snap.expression
    assert loaded.description == snap.description
    assert loaded.occurrences == snap.occurrences
    assert loaded.label == snap.label
