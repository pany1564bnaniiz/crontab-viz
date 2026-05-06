"""Utility helpers for analysing schedule overlap statistics."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Sequence

from .parser import parse
from .timeline import next_occurrences


@dataclass
class OverlapStats:
    expr_a: str
    expr_b: str
    window_hours: int
    count_a: int
    count_b: int
    count_common: int

    @property
    def jaccard(self) -> float:
        """Jaccard similarity of the two occurrence sets."""
        union = self.count_a + self.count_b - self.count_common
        return self.count_common / union if union else 1.0

    def __str__(self) -> str:
        return (
            f"{self.expr_a!r} vs {self.expr_b!r} over {self.window_hours}h: "
            f"A={self.count_a}, B={self.count_b}, "
            f"common={self.count_common}, jaccard={self.jaccard:.2f}"
        )


def overlap_in_window(
    expr_a: str,
    expr_b: str,
    window_hours: int = 24,
    now: datetime | None = None,
) -> OverlapStats:
    """Return overlap statistics within a fixed time window."""
    if now is None:
        now = datetime.now().replace(second=0, microsecond=0)

    end = now + timedelta(hours=window_hours)
    # Use a generous upper bound for occurrences
    big_count = window_hours * 60 + 1

    cron_a = parse(expr_a)
    cron_b = parse(expr_b)

    def _in_window(times: List[datetime]) -> List[datetime]:
        return [t for t in times if now <= t < end]

    times_a = set(_in_window(next_occurrences(cron_a, count=big_count, now=now)))
    times_b = set(_in_window(next_occurrences(cron_b, count=big_count, now=now)))

    return OverlapStats(
        expr_a=expr_a,
        expr_b=expr_b,
        window_hours=window_hours,
        count_a=len(times_a),
        count_b=len(times_b),
        count_common=len(times_a & times_b),
    )
