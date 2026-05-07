"""Render an hour-of-day × day-of-week heatmap for a cron expression."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List

from .parser import parse, ParseError
from .timeline import next_occurrences
from .colors import bold, dim, _wrap, RESET

_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
_HEAT_CHARS = [" ", "░", "▒", "▓", "█"]


@dataclass
class HeatmapData:
    expression: str
    # grid[day_of_week 0=Mon][hour 0-23] = count
    grid: List[List[int]] = field(default_factory=lambda: [[0] * 24 for _ in range(7)])
    max_count: int = 0

    def cell(self, dow: int, hour: int) -> int:
        return self.grid[dow][hour]


def build_heatmap(expression: str, weeks: int = 4) -> HeatmapData:
    """Count occurrences per (day-of-week, hour) over *weeks* weeks."""
    try:
        cron = parse(expression)
    except ParseError as exc:
        raise ValueError(str(exc)) from exc

    now = datetime.now().replace(second=0, microsecond=0)
    end = now + timedelta(weeks=weeks)
    # Estimate upper bound: at most once per minute → weeks*7*24*60
    count = weeks * 7 * 24 * 60 + 1
    occurrences = next_occurrences(cron, now, count)

    data = HeatmapData(expression=expression)
    for dt in occurrences:
        if dt >= end:
            break
        dow = dt.weekday()  # 0=Monday
        hour = dt.hour
        data.grid[dow][hour] += 1

    data.max_count = max(c for row in data.grid for c in row)
    return data


def _heat_char(value: int, max_val: int) -> str:
    if max_val == 0:
        return _HEAT_CHARS[0]
    idx = round(value / max_val * (len(_HEAT_CHARS) - 1))
    return _HEAT_CHARS[idx]


def render_heatmap(data: HeatmapData) -> str:
    """Return a multi-line string heatmap table."""
    lines: list[str] = []
    header_hours = "".join(f"{h:2}" for h in range(0, 24, 2))
    lines.append(bold(f"Heatmap: {data.expression}"))
    lines.append(dim("     " + header_hours))
    lines.append(dim("     " + "--" * 12))

    for dow_idx, day in enumerate(_DAYS):
        row_chars = ""
        for hour in range(24):
            val = data.grid[dow_idx][hour]
            ch = _heat_char(val, data.max_count)
            # colour: dim for empty, normal for active
            row_chars += dim(ch) if val == 0 else _wrap("33", ch + ch[0])[:-1] if False else ch + ch
        lines.append(f"  {day}  {row_chars}")

    lines.append(dim(f"  (over {data.max_count} max hits per cell)"))
    return "\n".join(lines)
