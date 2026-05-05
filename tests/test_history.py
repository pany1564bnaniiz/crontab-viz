"""Tests for crontab_viz.history."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from crontab_viz.history import (
    MAX_HISTORY,
    clear,
    load_history,
    recent_expressions,
    record,
)


@pytest.fixture()
def hist_file(tmp_path: Path) -> Path:
    return tmp_path / "history.json"


def test_record_creates_file(hist_file: Path) -> None:
    record("* * * * *", path=hist_file)
    assert hist_file.exists()


def test_record_stores_expression(hist_file: Path) -> None:
    record("0 9 * * 1-5", path=hist_file)
    entries = load_history(hist_file)
    assert entries[0]["expression"] == "0 9 * * 1-5"


def test_record_stores_timestamp(hist_file: Path) -> None:
    record("*/5 * * * *", path=hist_file)
    entries = load_history(hist_file)
    assert "recorded_at" in entries[0]
    assert entries[0]["recorded_at"].endswith("Z")


def test_record_deduplicates(hist_file: Path) -> None:
    record("* * * * *", path=hist_file)
    record("0 0 * * *", path=hist_file)
    record("* * * * *", path=hist_file)
    expressions = recent_expressions(path=hist_file)
    assert expressions.count("* * * * *") == 1


def test_record_newest_first(hist_file: Path) -> None:
    record("0 0 * * *", path=hist_file)
    record("*/10 * * * *", path=hist_file)
    expressions = recent_expressions(path=hist_file)
    assert expressions[0] == "*/10 * * * *"


def test_record_caps_at_max(hist_file: Path) -> None:
    for i in range(MAX_HISTORY + 10):
        record(f"{i % 60} * * * *", path=hist_file)
    assert len(load_history(hist_file)) <= MAX_HISTORY


def test_clear_removes_all(hist_file: Path) -> None:
    record("* * * * *", path=hist_file)
    clear(hist_file)
    assert load_history(hist_file) == []


def test_load_history_missing_file(hist_file: Path) -> None:
    assert load_history(hist_file) == []


def test_load_history_corrupt_file(hist_file: Path) -> None:
    hist_file.write_text("not json", encoding="utf-8")
    assert load_history(hist_file) == []


def test_recent_expressions_limit(hist_file: Path) -> None:
    for i in range(20):
        record(f"{i} * * * *", path=hist_file)
    result = recent_expressions(n=5, path=hist_file)
    assert len(result) == 5
