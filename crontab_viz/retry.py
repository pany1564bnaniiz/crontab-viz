"""Retry policy analysis for cron expressions.

Given a cron expression and a retry interval (in minutes), compute
whether retries could overlap with the next scheduled run.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

from .parser import parse, ParseError
from .timeline import next_occurrences


@dataclass
class RetryConflict:
    """A detected overlap between a retry window and a scheduled run."""
    scheduled_run: datetime
    retry_origin: datetime
    retry_attempt: int  # 1-based
    overlap_seconds: float

    def __str__(self) -> str:
        return (
            f"Retry #{self.retry_attempt} from {self.retry_origin:%H:%M} "
            f"overlaps scheduled run at {self.scheduled_run:%H:%M} "
            f"(+{self.overlap_seconds:.0f}s)"
        )


@dataclass
class RetryAnalysis:
    expression: str
    retry_interval_minutes: int
    max_retries: int
    conflicts: List[RetryConflict] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.error is None

    @property
    def has_conflicts(self) -> bool:
        return bool(self.conflicts)

    def summary(self) -> str:
        if not self.ok:
            return f"Error: {self.error}"
        if not self.has_conflicts:
            return (
                f"No retry conflicts detected "
            f"(interval={self.retry_interval_minutes}m, max={self.max_retries})"
            )
        lines = [
            f"{len(self.conflicts)} conflict(s) detected "
            f"(interval={self.retry_interval_minutes}m, max={self.max_retries}):"
        ]
        for c in self.conflicts:
            lines.append(f"  • {c}")
        return "\n".join(lines)


def analyze_retry(
    expression: str,
    retry_interval_minutes: int = 5,
    max_retries: int = 3,
    window: int = 24,
    now: Optional[datetime] = None,
) -> RetryAnalysis:
    """Analyse whether retry attempts could collide with future scheduled runs.

    Args:
        expression: cron expression string.
        retry_interval_minutes: minutes between retry attempts.
        max_retries: maximum number of retries after the initial run.
        window: how many upcoming occurrences to inspect.
        now: reference datetime (defaults to utcnow).
    """
    analysis = RetryAnalysis(
        expression=expression,
        retry_interval_minutes=retry_interval_minutes,
        max_retries=max_retries,
    )
    try:
        cron = parse(expression)
    except ParseError as exc:
        analysis.error = str(exc)
        return analysis

    if retry_interval_minutes < 1:
        analysis.error = "retry_interval_minutes must be >= 1"
        return analysis
    if max_retries < 1:
        analysis.error = "max_retries must be >= 1"
        return analysis

    base = now or datetime.utcnow()
    occurrences = next_occurrences(cron, count=window, now=base)

    scheduled_set = set(occurrences)
    delta = timedelta(minutes=retry_interval_minutes)

    for origin in occurrences:
        for attempt in range(1, max_retries + 1):
            retry_time = origin + delta * attempt
            if retry_time in scheduled_set:
                diff = (retry_time - origin).total_seconds()
                analysis.conflicts.append(
                    RetryConflict(
                        scheduled_run=retry_time,
                        retry_origin=origin,
                        retry_attempt=attempt,
                        overlap_seconds=diff,
                    )
                )

    return analysis
