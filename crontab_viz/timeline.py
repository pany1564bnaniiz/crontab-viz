"""Timeline rendering for crontab expressions."""

from datetime import datetime, timedelta
from typing import List

from .parser import CronExpression


def next_occurrences(
    expr: CronExpression,
    start: datetime,
    count: int = 10,
) -> List[datetime]:
    """Return the next `count` datetimes matching the cron expression."""
    results = []
    current = start.replace(second=0, microsecond=0) + timedelta(minutes=1)
    limit = start + timedelta(days=366)

    while len(results) < count and current < limit:
        if (
            current.month in expr.month
            and current.day in expr.day_of_month
            and current.weekday() % 7 in _weekday_map(expr.day_of_week)
            and current.hour in expr.hour
            and current.minute in expr.minute
        ):
            results.append(current)
        current += timedelta(minutes=1)

    return results


def _weekday_map(dow_values: List[int]) -> List[int]:
    """Convert cron DOW (0=Sun) to Python weekday (0=Mon)."""
    mapping = {0: 6, 1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5}
    return [mapping[d] for d in dow_values]


def render_timeline(expr: CronExpression, start: datetime, count: int = 10) -> str:
    """Render a human-readable timeline of upcoming cron occurrences."""
    occurrences = next_occurrences(expr, start, count)
    lines = [
        f"Schedule for: {expr.raw}",
        f"Starting from: {start.strftime('%Y-%m-%d %H:%M')}",
        "-" * 40,
    ]

    if not occurrences:
        lines.append("  (no occurrences found in the next year)")
    else:
        for i, dt in enumerate(occurrences, 1):
            delta = dt - start
            hours, remainder = divmod(int(delta.total_seconds()), 3600)
            minutes = remainder // 60
            relative = _format_relative(hours, minutes)
            lines.append(f"  {i:>2}. {dt.strftime('%Y-%m-%d %H:%M')}  ({relative})")

    lines.append("-" * 40)
    return "\n".join(lines)


def _format_relative(hours: int, minutes: int) -> str:
    if hours == 0 and minutes == 0:
        return "now"
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    return "in " + " ".join(parts)
