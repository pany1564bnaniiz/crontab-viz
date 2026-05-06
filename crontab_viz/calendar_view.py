"""Render a monthly calendar view showing cron fire days."""
from __future__ import annotations

import calendar
from datetime import datetime, date
from typing import List, Set

from .parser import parse, ParseError
from .timeline import next_occurrences
from .colors import bold, green, dim, yellow

__all__ = ["CalendarView", "build_calendar", "render_calendar"]


class CalendarView:
    """Holds fire-day data for a single month."""

    def __init__(self, year: int, month: int, fire_days: Set[int]) -> None:
        self.year = year
        self.month = month
        self.fire_days = fire_days

    @property
    def month_name(self) -> str:
        return calendar.month_name[self.month]

    def __repr__(self) -> str:  # pragma: no cover
        return f"CalendarView({self.year}, {self.month}, fire_days={sorted(self.fire_days)})"


def build_calendar(
    expression: str,
    year: int | None = None,
    month: int | None = None,
    *,
    lookahead: int = 1500,
) -> CalendarView:
    """Return a CalendarView for *expression* in the given month.

    Raises ParseError if the expression is invalid.
    """
    cron = parse(expression)
    now = datetime.now()
    year = year or now.year
    month = month or now.month

    start = datetime(year, month, 1, 0, 0, 0)
    _, last_day = calendar.monthrange(year, month)
    end = datetime(year, month, last_day, 23, 59, 59)

    occurrences: List[datetime] = next_occurrences(cron, count=lookahead, start=start)
    fire_days: Set[int] = {
        dt.day for dt in occurrences if start <= dt <= end
    }
    return CalendarView(year, month, fire_days)


def render_calendar(view: CalendarView) -> str:
    """Return a formatted string calendar for the given CalendarView."""
    header = bold(f"  {view.month_name} {view.year}")
    week_header = dim("Mo Tu We Th Fr Sa Su")
    lines = [header, week_header]

    cal = calendar.monthcalendar(view.year, view.month)
    today = date.today()

    for week in cal:
        cells = []
        for day in week:
            if day == 0:
                cells.append("  ")
            elif day in view.fire_days:
                token = f"{day:2d}"
                if date(view.year, view.month, day) == today:
                    token = yellow(token)
                else:
                    token = green(token)
                cells.append(token)
            else:
                token = f"{day:2d}"
                if date(view.year, view.month, day) == today:
                    token = bold(token)
                cells.append(token)
        lines.append(" ".join(cells))

    return "\n".join(lines)
