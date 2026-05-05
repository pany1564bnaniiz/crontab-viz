"""Converts cron expressions into plain-English next-run summaries."""

from datetime import datetime, timedelta
from typing import Optional

from .timeline import next_occurrences
from .parser import parse, ParseError


def _delta_to_words(delta: timedelta) -> str:
    """Turn a timedelta into a short human-readable string."""
    total_seconds = int(delta.total_seconds())
    if total_seconds < 60:
        return f"{total_seconds} second{'s' if total_seconds != 1 else ''}"
    minutes = total_seconds // 60
    if minutes < 60:
        return f"{minutes} minute{'s' if minutes != 1 else ''}"
    hours = minutes // 60
    remaining_minutes = minutes % 60
    if hours < 24:
        parts = [f"{hours} hour{'s' if hours != 1 else ''}"]
        if remaining_minutes:
            parts.append(f"{remaining_minutes} minute{'s' if remaining_minutes != 1 else ''}")
        return " and ".join(parts)
    days = hours // 24
    remaining_hours = hours % 24
    parts = [f"{days} day{'s' if days != 1 else ''}"]
    if remaining_hours:
        parts.append(f"{remaining_hours} hour{'s' if remaining_hours != 1 else ''}")
    return " and ".join(parts)


def _plural(count: int, singular: str, plural: Optional[str] = None) -> str:
    """Return *singular* or *plural* form based on *count*.

    If *plural* is not provided, an ``'s'`` suffix is appended to *singular*.
    """
    if count == 1:
        return singular
    return plural if plural is not None else f"{singular}s"


def next_run_summary(
    expression: str,
    now: Optional[datetime] = None,
    count: int = 3,
) -> str:
    """Return a plain-English summary of the next *count* runs.

    Parameters
    ----------
    expression:
        A crontab expression string (5 fields or an alias such as ``@hourly``).
    now:
        Reference time; defaults to ``datetime.now()`` when *None*.
    count:
        How many upcoming occurrences to include in the summary.

    Returns
    -------
    str
        Multi-line human-readable text.
    """
    if now is None:
        now = datetime.now().replace(second=0, microsecond=0)

    try:
        expr = parse(expression)
    except ParseError as exc:
        return f"Invalid expression: {exc}"

    occurrences = next_occurrences(expr, now=now, count=count)
    if not occurrences:
        return "No upcoming occurrences found."

    lines = [f"Next {len(occurrences)} {_plural(len(occurrences), 'run')}:"]
    for occ in occurrences:
        delta = occ - now
        when = occ.strftime("%Y-%m-%d %H:%M")
        lines.append(f"  {when}  (in {_delta_to_words(delta)})")
    return "\n".join(lines)
