"""Tests for crontab_viz.calendar_view."""
from __future__ import annotations

from datetime import datetime
from unittest.mock import patch

import pytest

from crontab_viz.calendar_view import build_calendar, render_calendar, CalendarView
from crontab_viz.parser import ParseError


# ---------------------------------------------------------------------------
# build_calendar
# ---------------------------------------------------------------------------

def test_build_calendar_returns_calendar_view():
    view = build_calendar("0 9 * * *", year=2024, month=1)
    assert isinstance(view, CalendarView)


def test_build_calendar_correct_year_month():
    view = build_calendar("0 9 * * *", year=2024, month=3)
    assert view.year == 2024
    assert view.month == 3


def test_build_calendar_daily_fires_every_day():
    view = build_calendar("0 9 * * *", year=2024, month=1)
    # January has 31 days; daily cron should fire each one
    assert len(view.fire_days) == 31
    assert view.fire_days == set(range(1, 32))


def test_build_calendar_monthly_fires_once():
    view = build_calendar("0 9 15 * *", year=2024, month=1)
    assert view.fire_days == {15}


def test_build_calendar_every_minute_fires_every_day():
    view = build_calendar("* * * * *", year=2024, month=2)
    # Feb 2024 has 29 days (leap year)
    assert len(view.fire_days) == 29


def test_build_calendar_invalid_expression_raises():
    with pytest.raises(ParseError):
        build_calendar("not valid", year=2024, month=1)


def test_build_calendar_uses_current_date_defaults():
    fixed = datetime(2025, 6, 1)
    with patch("crontab_viz.calendar_view.datetime") as mock_dt:
        mock_dt.now.return_value = fixed
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
        view = build_calendar("0 0 * * *")
    assert view.year == 2025
    assert view.month == 6


def test_build_calendar_alias():
    view = build_calendar("@daily", year=2024, month=4)
    assert len(view.fire_days) == 30  # April has 30 days


# ---------------------------------------------------------------------------
# render_calendar
# ---------------------------------------------------------------------------

def test_render_calendar_contains_month_name():
    view = CalendarView(2024, 1, {1, 15, 31})
    output = render_calendar(view)
    assert "January" in output


def test_render_calendar_contains_year():
    view = CalendarView(2024, 1, {1})
    output = render_calendar(view)
    assert "2024" in output


def test_render_calendar_contains_day_numbers():
    view = CalendarView(2024, 1, set())
    output = render_calendar(view)
    assert "15" in output


def test_render_calendar_has_seven_lines_of_weeks():
    view = CalendarView(2024, 1, set())
    output = render_calendar(view)
    lines = output.strip().splitlines()
    # header + weekday row + up to 6 week rows
    assert len(lines) >= 3


def test_calendar_view_month_name_property():
    view = CalendarView(2024, 7, set())
    assert view.month_name == "July"
