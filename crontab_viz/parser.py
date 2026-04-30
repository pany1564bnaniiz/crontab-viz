"""Crontab expression parser module."""

from dataclasses import dataclass
from typing import List, Optional


CRON_FIELDS = ["minute", "hour", "day_of_month", "month", "day_of_week"]

FIELD_RANGES = {
    "minute": (0, 59),
    "hour": (0, 23),
    "day_of_month": (1, 31),
    "month": (1, 12),
    "day_of_week": (0, 6),
}

MONTH_ALIASES = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "may": 5, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

DOW_ALIASES = {
    "sun": 0, "mon": 1, "tue": 2, "wed": 3,
    "thu": 4, "fri": 5, "sat": 6,
}


@dataclass
class CronExpression:
    minute: List[int]
    hour: List[int]
    day_of_month: List[int]
    month: List[int]
    day_of_week: List[int]
    raw: str


class ParseError(ValueError):
    pass


def _resolve_alias(value: str, field: str) -> str:
    lower = value.lower()
    if field == "month" and lower in MONTH_ALIASES:
        return str(MONTH_ALIASES[lower])
    if field == "day_of_week" and lower in DOW_ALIASES:
        return str(DOW_ALIASES[lower])
    return value


def _parse_field(field_str: str, field: str) -> List[int]:
    min_val, max_val = FIELD_RANGES[field]
    values = set()

    for part in field_str.split(","):
        part = _resolve_alias(part, field)
        if part == "*":
            values.update(range(min_val, max_val + 1))
        elif "/" in part:
            base, step_str = part.split("/", 1)
            step = int(step_str)
            start = min_val if base == "*" else int(base.split("-")[0])
            end = max_val if base == "*" else (int(base.split("-")[1]) if "-" in base else max_val)
            values.update(range(start, end + 1, step))
        elif "-" in part:
            start, end = part.split("-", 1)
            values.update(range(int(start), int(end) + 1))
        else:
            values.add(int(part))

    result = sorted(v for v in values if min_val <= v <= max_val)
    if not result:
        raise ParseError(f"No valid values for field '{field}' in '{field_str}'")
    return result


def parse(expression: str) -> CronExpression:
    """Parse a crontab expression string into a CronExpression."""
    parts = expression.strip().split()
    if len(parts) != 5:
        raise ParseError(f"Expected 5 fields, got {len(parts)}: '{expression}'")

    parsed = {}
    for field, value in zip(CRON_FIELDS, parts):
        try:
            parsed[field] = _parse_field(value, field)
        except (ValueError, IndexError) as exc:
            raise ParseError(f"Invalid value for '{field}': {value}") from exc

    return CronExpression(raw=expression, **parsed)
