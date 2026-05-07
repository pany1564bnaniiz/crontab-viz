"""Detect burst periods — windows where a cron expression fires more than a
threshold number of times within a rolling duration."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

from .parser import parse, ParseError
from .timeline import next_occurrences


@dataclass
class BurstWindow:
    start: datetime
    end: datetime
    count: int
    occurrences: List[datetime] = field(default_factory=list)

    def duration_seconds(self) -> float:
        return (self.end - self.start).total_seconds()

    def __str__(self) -> str:  # pragma: no cover
        fmt = "%Y-%m-%d %H:%M"
        return (
            f"{self.start.strftime(fmt)} – {self.end.strftime(fmt)}: "
            f"{self.count} fires"
        )


@dataclass
class BurstResult:
    expression: str
    window_seconds: int
    threshold: int
    bursts: List[BurstWindow] = field(default_factory=list)
    error: Optional[str] = None

    def ok(self) -> bool:
        return self.error is None

    def summary(self) -> str:
        if self.error:
            return f"Error: {self.error}"
        if not self.bursts:
            return (
                f"No burst windows found (threshold={self.threshold}, "
                f"window={self.window_seconds}s)."
            )
        return (
            f"{len(self.bursts)} burst window(s) detected where fires >= "
            f"{self.threshold} within {self.window_seconds}s."
        )


def detect_bursts(
    expression: str,
    *,
    window_seconds: int = 3600,
    threshold: int = 10,
    lookahead: int = 500,
    since: Optional[datetime] = None,
) -> BurstResult:
    """Return a BurstResult describing windows where *expression* fires
    >= *threshold* times within a rolling *window_seconds* window."""
    result = BurstResult(
        expression=expression,
        window_seconds=window_seconds,
        threshold=threshold,
    )
    try:
        cron = parse(expression)
    except ParseError as exc:
        result.error = str(exc)
        return result

    base = since or datetime.now().replace(second=0, microsecond=0)
    times = next_occurrences(cron, count=lookahead, since=base)

    window = timedelta(seconds=window_seconds)
    seen_starts: set = set()

    for i, t in enumerate(times):
        bucket = [t2 for t2 in times[i:] if t2 - t <= window]
        if len(bucket) >= threshold:
            key = bucket[0]
            if key not in seen_starts:
                seen_starts.add(key)
                result.bursts.append(
                    BurstWindow(
                        start=bucket[0],
                        end=bucket[-1],
                        count=len(bucket),
                        occurrences=bucket,
                    )
                )
    return result
