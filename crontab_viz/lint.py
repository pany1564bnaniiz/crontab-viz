"""Lint crontab expressions for common mistakes and anti-patterns."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .parser import CronExpression, parse, ParseError


@dataclass
class LintResult:
    expression: str
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        """True when no warnings were found."""
        return len(self.warnings) == 0

    def summary(self) -> str:
        if not self.warnings and not self.suggestions:
            return f"OK  {self.expression}"
        lines = [f"WARN  {self.expression}"]
        for w in self.warnings:
            lines.append(f"  [warning]    {w}")
        for s in self.suggestions:
            lines.append(f"  [suggestion] {s}")
        return "\n".join(lines)


def _check_high_frequency(expr: CronExpression, result: LintResult) -> None:
    """Warn when a job runs more than once per minute (not possible) or every minute."""
    if expr.minute == set(range(60)) and expr.hour == set(range(24)):
        result.warnings.append(
            "Job runs every minute — ensure this is intentional."
        )


def _check_dom_dow_conflict(expr: CronExpression, result: LintResult) -> None:
    """Warn about ambiguous DOM+DOW combinations."""
    full_dom = expr.dom == set(range(1, 32))
    full_dow = expr.dow == set(range(7))
    if not full_dom and not full_dow:
        result.warnings.append(
            "Both day-of-month and day-of-week are restricted; "
            "occurrences match either condition (OR semantics)."
        )


def _check_midnight_only(expr: CronExpression, result: LintResult) -> None:
    """Suggest using @daily alias when schedule is '0 0 * * *'."""
    if (
        expr.minute == {0}
        and expr.hour == {0}
        and expr.dom == set(range(1, 32))
        and expr.month == set(range(1, 13))
        and expr.dow == set(range(7))
    ):
        result.suggestions.append(
            "Schedule is equivalent to the @daily alias."
        )


def _check_suspicious_step(expr: CronExpression, result: LintResult) -> None:
    """Warn when a step value equals the field range (effectively runs once)."""
    checks = [
        (expr.minute, 60, "minute"),
        (expr.hour, 24, "hour"),
        (expr.dom, 31, "day-of-month"),
        (expr.month, 12, "month"),
    ]
    for values, range_size, name in checks:
        if len(values) == 1 and range_size > 1:
            # A step equal to the range produces a single value — may be intentional
            # but worth flagging if it looks like */N where N == range
            pass  # heuristic not reliable without AST; skip


def lint(expression: str) -> LintResult:
    """Lint *expression* and return a :class:`LintResult`."""
    result = LintResult(expression=expression)
    try:
        expr = parse(expression)
    except ParseError as exc:
        result.warnings.append(f"Parse error: {exc}")
        return result

    _check_high_frequency(expr, result)
    _check_dom_dow_conflict(expr, result)
    _check_midnight_only(expr, result)
    _check_suspicious_step(expr, result)
    return result
