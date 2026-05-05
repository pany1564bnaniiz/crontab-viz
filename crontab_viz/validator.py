"""Validates crontab expressions and provides detailed error messages."""

from dataclasses import dataclass
from typing import List, Optional
from .parser import ParseError, _parse_field, _resolve_alias

# Field constraints: (min, max, name)
FIELD_CONSTRAINTS = [
    (0, 59, "minute"),
    (0, 23, "hour"),
    (1, 31, "day-of-month"),
    (1, 12, "month"),
    (0, 7, "day-of-week"),
]

MONTH_NAMES = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "may": 5, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

WEEKDAY_NAMES = {
    "sun": 0, "mon": 1, "tue": 2, "wed": 3,
    "thu": 4, "fri": 5, "sat": 6,
}


@dataclass
class ValidationResult:
    valid: bool
    errors: List[str]
    warnings: List[str]

    def __bool__(self) -> bool:
        return self.valid


def _check_field(expr: str, min_val: int, max_val: int, name: str) -> List[str]:
    """Return a list of error strings for a single cron field."""
    errors = []
    try:
        values = _parse_field(expr, min_val, max_val)
        if not values:
            errors.append(f"{name}: expression '{expr}' matched no values in [{min_val},{max_val}]")
    except ParseError as exc:
        errors.append(f"{name}: {exc}")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"{name}: unexpected error — {exc}")
    return errors


def _dom_dow_warning(dom: str, dow: str) -> Optional[str]:
    """Warn when both day-of-month and day-of-week are restricted (non-wildcard)."""
    if dom not in ("*", "?") and dow not in ("*", "?"):
        return (
            "Both day-of-month and day-of-week are restricted; "
            "occurrences satisfy EITHER condition (union semantics)."
        )
    return None


def validate(expression: str) -> ValidationResult:
    """Validate a crontab expression string.

    Returns a :class:`ValidationResult` with `valid`, `errors`, and `warnings`.
    """
    errors: List[str] = []
    warnings: List[str] = []

    try:
        resolved = _resolve_alias(expression.strip())
    except ParseError as exc:
        return ValidationResult(valid=False, errors=[str(exc)], warnings=[])

    parts = resolved.split()
    if len(parts) != 5:
        errors.append(
            f"Expected 5 fields (minute hour dom month dow), got {len(parts)}."
        )
        return ValidationResult(valid=False, errors=errors, warnings=warnings)

    for part, (mn, mx, name) in zip(parts, FIELD_CONSTRAINTS):
        errors.extend(_check_field(part, mn, mx, name))

    warn = _dom_dow_warning(parts[2], parts[4])
    if warn:
        warnings.append(warn)

    return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)
