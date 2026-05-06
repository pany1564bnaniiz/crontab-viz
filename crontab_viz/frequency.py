"""Compute and compare execution frequency statistics for cron expressions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .parser import parse, ParseError
from .timeline import next_occurrences

# Seconds in common windows
_MINUTE = 60
_HOUR = 3_600
_DAY = 86_400
_WEEK = 604_800
_MONTH = 2_592_000  # 30 days


@dataclass
class FrequencyStats:
    expression: str
    runs_per_hour: float
    runs_per_day: float
    runs_per_week: float
    runs_per_month: float
    avg_interval_seconds: float
    label: str  # human-readable tier label

    def __str__(self) -> str:
        return (
            f"{self.expression!r} [{self.label}] "
            f"~{self.runs_per_day:.1f}/day, "
            f"avg interval {_fmt_interval(self.avg_interval_seconds)}"
        )


def _fmt_interval(seconds: float) -> str:
    if seconds < _MINUTE:
        return f"{int(seconds)}s"
    if seconds < _HOUR:
        return f"{seconds / _MINUTE:.1f}m"
    if seconds < _DAY:
        return f"{seconds / _HOUR:.1f}h"
    return f"{seconds / _DAY:.1f}d"


def _label(runs_per_day: float) -> str:
    if runs_per_day >= 1440:
        return "every-minute"
    if runs_per_day >= 24:
        return "high-frequency"
    if runs_per_day >= 1:
        return "daily"
    if runs_per_day >= 1 / 7:
        return "weekly"
    return "low-frequency"


def compute_frequency(expression: str, sample: int = 1440) -> FrequencyStats:
    """Derive frequency statistics by sampling *sample* occurrences.

    Raises ``ParseError`` if *expression* is invalid.
    """
    cron = parse(expression)  # raises ParseError on bad input
    occurrences = next_occurrences(cron, count=sample)
    if len(occurrences) < 2:
        raise ValueError("Not enough occurrences to compute frequency.")

    total_seconds = (occurrences[-1] - occurrences[0]).total_seconds()
    avg_interval = total_seconds / (len(occurrences) - 1)

    runs_per_hour = _HOUR / avg_interval
    runs_per_day = _DAY / avg_interval
    runs_per_week = _WEEK / avg_interval
    runs_per_month = _MONTH / avg_interval

    return FrequencyStats(
        expression=expression,
        runs_per_hour=runs_per_hour,
        runs_per_day=runs_per_day,
        runs_per_week=runs_per_week,
        runs_per_month=runs_per_month,
        avg_interval_seconds=avg_interval,
        label=_label(runs_per_day),
    )


def compare_frequencies(expressions: List[str], sample: int = 1440) -> List[FrequencyStats]:
    """Return a list of ``FrequencyStats`` sorted from most to least frequent."""
    stats = [compute_frequency(e, sample=sample) for e in expressions]
    return sorted(stats, key=lambda s: s.runs_per_day, reverse=True)
