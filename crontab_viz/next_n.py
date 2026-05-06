"""Compute and format the next N run times for one or more cron expressions."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from .parser import parse, ParseError
from .timeline import next_occurrences
from .humanize import next_run_summary


@dataclass
class NextNResult:
    expression: str
    occurrences: List[datetime] = field(default_factory=list)
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None


def compute(expression: str, count: int = 5, now: datetime | None = None) -> NextNResult:
    """Return the next *count* occurrences for *expression*.

    Args:
        expression: A standard five-field cron expression or alias.
        count:      How many future datetimes to compute (1-100).
        now:        Reference point; defaults to the current UTC time.

    Returns:
        A :class:`NextNResult` with either occurrences or an error message.
    """
    if count < 1 or count > 100:
        return NextNResult(expression=expression, error="count must be between 1 and 100")

    try:
        cron = parse(expression)
    except ParseError as exc:
        return NextNResult(expression=expression, error=str(exc))

    base = now or datetime.utcnow()
    times = next_occurrences(cron, count=count, now=base)
    return NextNResult(expression=expression, occurrences=times)


def format_next_n(result: NextNResult, now: datetime | None = None) -> str:
    """Render a :class:`NextNResult` as a human-readable string."""
    if not result.ok:
        return f"Error for '{result.expression}': {result.error}"

    base = now or datetime.utcnow()
    lines = [f"Next {len(result.occurrences)} runs for: {result.expression}"]
    lines.append("-" * 44)
    for i, dt in enumerate(result.occurrences, 1):
        rel = next_run_summary(dt, now=base)
        lines.append(f"  {i:>2}. {dt.strftime('%Y-%m-%d %H:%M')} UTC  ({rel})")
    return "\n".join(lines)


def compare_next_n(
    expressions: List[str],
    count: int = 5,
    now: datetime | None = None,
) -> List[NextNResult]:
    """Compute next occurrences for multiple expressions at once."""
    base = now or datetime.utcnow()
    return [compute(expr, count=count, now=base) for expr in expressions]
