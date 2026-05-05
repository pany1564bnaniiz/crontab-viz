"""Tests for crontab_viz.interactive."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from crontab_viz.history import record
from crontab_viz.interactive import _render_history_table, pick_from_history, print_history


@pytest.fixture()
def populated_history(tmp_path: Path) -> Path:
    hist = tmp_path / "history.json"
    for expr in ["* * * * *", "0 9 * * 1-5", "*/15 * * * *"]:
        record(expr, path=hist)
    return hist


def test_render_table_empty() -> None:
    result = _render_history_table([])
    assert "no history" in result


def test_render_table_contains_expressions(populated_history: Path) -> None:
    from crontab_viz.history import load_history

    entries = load_history(populated_history)
    table = _render_history_table(entries)
    assert "* * * * *" in table
    assert "0 9 * * 1-5" in table


def test_render_table_row_count(populated_history: Path) -> None:
    from crontab_viz.history import load_history

    entries = load_history(populated_history)
    table = _render_history_table(entries)
    # Each expression should appear once
    for entry in entries:
        assert entry["expression"] in table


def test_print_history_outputs_text(capsys, populated_history: Path) -> None:
    print_history(n=10, path=populated_history)
    captured = capsys.readouterr()
    assert "Recent crontab" in captured.out


def test_pick_from_history_valid_choice(populated_history: Path) -> None:
    with patch("builtins.input", return_value="1"):
        result = pick_from_history(n=10, path=populated_history)
    # Most recent entry is first
    assert result == "*/15 * * * *"


def test_pick_from_history_cancel_blank(populated_history: Path) -> None:
    with patch("builtins.input", return_value=""):
        result = pick_from_history(n=10, path=populated_history)
    assert result is None


def test_pick_from_history_cancel_eof(populated_history: Path) -> None:
    with patch("builtins.input", side_effect=EOFError):
        result = pick_from_history(n=10, path=populated_history)
    assert result is None


def test_pick_from_history_out_of_range(capsys, populated_history: Path) -> None:
    with patch("builtins.input", return_value="99"):
        result = pick_from_history(n=10, path=populated_history)
    assert result is None
    captured = capsys.readouterr()
    assert "range" in captured.out


def test_pick_from_history_no_history(tmp_path: Path) -> None:
    empty = tmp_path / "empty.json"
    result = pick_from_history(path=empty)
    assert result is None
