"""Export crontab schedule data to JSON or CSV formats."""

import csv
import json
import io
from datetime import datetime
from typing import List

from crontab_viz.parser import CronExpression
from crontab_viz.timeline import next_occurrences
from crontab_viz.formatter import describe


def to_json(expr: CronExpression, raw: str, count: int = 10, base: datetime = None) -> str:
    """Serialize the next `count` occurrences to a JSON string."""
    base = base or datetime.now()
    occurrences = next_occurrences(expr, base, count)
    payload = {
        "expression": raw,
        "description": describe(expr),
        "base": base.isoformat(),
        "occurrences": [dt.isoformat() for dt in occurrences],
    }
    return json.dumps(payload, indent=2)


def to_csv(expr: CronExpression, raw: str, count: int = 10, base: datetime = None) -> str:
    """Serialize the next `count` occurrences to a CSV string."""
    base = base or datetime.now()
    occurrences = next_occurrences(expr, base, count)
    description = describe(expr)

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["expression", "description", "occurrence"])
    for dt in occurrences:
        writer.writerow([raw, description, dt.isoformat()])
    return buf.getvalue()


def export(expr: CronExpression, raw: str, fmt: str, count: int = 10, base: datetime = None) -> str:
    """Dispatch export to the correct format handler."""
    fmt = fmt.lower()
    if fmt == "json":
        return to_json(expr, raw, count, base)
    if fmt == "csv":
        return to_csv(expr, raw, count, base)
    raise ValueError(f"Unsupported export format: {fmt!r}. Choose 'json' or 'csv'.")
