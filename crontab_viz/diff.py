"""Compare two crontab expressions and summarize their differences."""

from dataclasses import dataclass
from typing import List

from .parser import parse, CronExpression
from .formatter import describe


@dataclass
class DiffResult:
    expr_a: str
    expr_b: str
    description_a: str
    description_b: str
    changed_fields: List[str]
    same: bool

    def summary(self) -> str:
        if self.same:
            return "Expressions are equivalent."
        lines = [
            f"A: {self.expr_a}  →  {self.description_a}",
            f"B: {self.expr_b}  →  {self.description_b}",
            "Changed fields: " + ", ".join(self.changed_fields),
        ]
        return "\n".join(lines)


_FIELD_NAMES = ["minute", "hour", "dom", "month", "dow"]


def _field_values(expr: CronExpression) -> List[frozenset]:
    return [
        frozenset(expr.minute),
        frozenset(expr.hour),
        frozenset(expr.dom),
        frozenset(expr.month),
        frozenset(expr.dow),
    ]


def diff(expr_a: str, expr_b: str) -> DiffResult:
    """Compare two cron expressions and return a DiffResult.

    Args:
        expr_a: The first cron expression string.
        expr_b: The second cron expression string.

    Returns:
        A DiffResult describing which fields changed and human-readable
        descriptions of both expressions.

    Raises:
        ValueError: If either expression cannot be parsed.
    """
    cron_a = parse(expr_a)
    cron_b = parse(expr_b)

    values_a = _field_values(cron_a)
    values_b = _field_values(cron_b)

    changed = [
        name
        for name, va, vb in zip(_FIELD_NAMES, values_a, values_b)
        if va != vb
    ]

    return DiffResult(
        expr_a=expr_a,
        expr_b=expr_b,
        description_a=describe(cron_a),
        description_b=describe(cron_b),
        changed_fields=changed,
        same=len(changed) == 0,
    )
