"""Tests for crontab_viz.heatmap and crontab_viz.heatmap_cli."""
from __future__ import annotations

import pytest

from crontab_viz.heatmap import build_heatmap, render_heatmap, HeatmapData, _heat_char
from crontab_viz.heatmap_cli import build_parser, main


# ---------------------------------------------------------------------------
# build_heatmap
# ---------------------------------------------------------------------------

def test_build_heatmap_returns_heatmap_data():
    data = build_heatmap("* * * * *", weeks=1)
    assert isinstance(data, HeatmapData)


def test_build_heatmap_expression_stored():
    data = build_heatmap("0 * * * *", weeks=1)
    assert data.expression == "0 * * * *"


def test_build_heatmap_grid_shape():
    data = build_heatmap("0 9 * * *", weeks=2)
    assert len(data.grid) == 7
    assert all(len(row) == 24 for row in data.grid)


def test_build_heatmap_daily_fires_every_day():
    """Daily at 09:00 → each weekday row should have a hit in hour 9."""
    data = build_heatmap("0 9 * * *", weeks=4)
    for dow in range(7):
        assert data.grid[dow][9] > 0


def test_build_heatmap_hourly_max_count():
    data = build_heatmap("0 * * * *", weeks=1)
    assert data.max_count > 0


def test_build_heatmap_invalid_expression_raises():
    with pytest.raises(ValueError):
        build_heatmap("invalid", weeks=1)


def test_build_heatmap_weekly_fires_once_per_week():
    """@weekly (0 0 * * 0) fires on Sunday only."""
    data = build_heatmap("0 0 * * 0", weeks=4)
    # Sunday is weekday index 6 in Python
    assert data.grid[6][0] > 0
    # No other day should fire
    for dow in range(6):
        assert data.grid[dow][0] == 0


# ---------------------------------------------------------------------------
# _heat_char
# ---------------------------------------------------------------------------

def test_heat_char_zero_max():
    assert _heat_char(0, 0) == " "


def test_heat_char_full():
    from crontab_viz.heatmap import _HEAT_CHARS
    assert _heat_char(10, 10) == _HEAT_CHARS[-1]


def test_heat_char_zero_value():
    from crontab_viz.heatmap import _HEAT_CHARS
    assert _heat_char(0, 10) == _HEAT_CHARS[0]


# ---------------------------------------------------------------------------
# render_heatmap
# ---------------------------------------------------------------------------

def test_render_heatmap_returns_string():
    data = build_heatmap("0 9 * * *", weeks=1)
    result = render_heatmap(data)
    assert isinstance(result, str)


def test_render_heatmap_contains_all_days():
    data = build_heatmap("0 9 * * *", weeks=1)
    result = render_heatmap(data)
    for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
        assert day in result


def test_render_heatmap_contains_expression():
    expr = "30 6 * * 1-5"
    data = build_heatmap(expr, weeks=2)
    result = render_heatmap(data)
    assert expr in result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def test_build_parser_defaults():
    parser = build_parser()
    args = parser.parse_args(["0 * * * *"])
    assert args.weeks == 4
    assert args.no_color is False


def test_build_parser_custom_weeks():
    parser = build_parser()
    args = parser.parse_args(["0 * * * *", "--weeks", "8"])
    assert args.weeks == 8


def test_main_valid_expression_exits_zero(capsys):
    rc = main(["0 9 * * *"])
    assert rc == 0


def test_main_output_contains_days(capsys):
    main(["0 9 * * *", "--no-color"])
    out = capsys.readouterr().out
    assert "Mon" in out


def test_main_invalid_expression_exits_nonzero(capsys):
    rc = main(["not_a_cron"])
    assert rc == 1


def test_main_weeks_out_of_range_exits_nonzero(capsys):
    rc = main(["0 * * * *", "--weeks", "0"])
    assert rc == 1
