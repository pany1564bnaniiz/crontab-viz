"""Compare two cron schedules by their next N occurrences."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Tuple

from .parser import parse, CronExpression
from .timeline import next_occurrences


@dataclass
class ScheduleCompareResult:
    expr_a: str
    expr_b: str
    only_in_a: List[datetime] = field(default_factory=list)
    only_in_b: List[datetime] = field(default_factory=list)
    common: List[datetime] = field(default_factory=list)

    @property
    def overlap_ratio(self) -> float:
        """Fraction of combined unique times that are shared."""
        total = len(self.only_in_a) + len(self.only_in_b) + len(self.common)
        if total == 0:
            return 1.0
        return len(self.common) / total

    def summary(self) -> str:
        lines = [
            f"Schedule A : {self.expr_a}",
            f"Schedule B : {self.expr_b}",
            f"Common     : {len(self.common)}",
            f"Only in A  : {len(self.only_in_a)}",
            f"Only in B  : {len(self.only_in_b)}",
            f"Overlap    : {self.overlap_ratio:.0%}",
        ]
        return "\n".join(lines)


def compare_schedules(
    expr_a: str,
    expr_b: str,
    count: int = 20,
    now: datetime | None = None,
) -> ScheduleCompareResult:
    """Compare next *count* occurrences of two cron expressions."""
    if now is None:
        now = datetime.now().replace(second=0, microsecond=0)

    cron_a: CronExpression = parse(expr_a)
    cron_b: CronExpression = parse(expr_b)

    times_a = set(next_occurrences(cron_a, count=count, now=now))
    times_b = set(next_occurrences(cron_b, count=count, now=now))

    common = sorted(times_a & times_b)
    only_a = sorted(times_a - times_b)
    only_b = sorted(times_b - times_a)

    return ScheduleCompareResult(
        expr_a=expr_a,
        expr_b=expr_b,
        only_in_a=only_a,
        only_in_b=only_b,
        common=common,
    )
