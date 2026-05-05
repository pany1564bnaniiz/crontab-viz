"""Predefined cron expression templates with metadata."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Template:
    name: str
    expression: str
    description: str
    category: str
    tags: List[str]


_TEMPLATES: List[Template] = [
    Template("every_minute", "* * * * *", "Every minute", "frequent", ["frequent", "debug"]),
    Template("every_5_minutes", "*/5 * * * *", "Every 5 minutes", "frequent", ["frequent"]),
    Template("every_15_minutes", "*/15 * * * *", "Every 15 minutes", "frequent", ["frequent"]),
    Template("every_30_minutes", "*/30 * * * *", "Every 30 minutes", "frequent", ["frequent"]),
    Template("hourly", "@hourly", "Once an hour at the top", "hourly", ["hourly"]),
    Template("every_2_hours", "0 */2 * * *", "Every 2 hours", "hourly", ["hourly"]),
    Template("daily_midnight", "@daily", "Once a day at midnight", "daily", ["daily"]),
    Template("daily_noon", "0 12 * * *", "Every day at noon", "daily", ["daily"]),
    Template("daily_6am", "0 6 * * *", "Every day at 6 AM", "daily", ["daily", "morning"]),
    Template("weekdays_9am", "0 9 * * 1-5", "Weekdays at 9 AM", "weekly", ["weekday", "business"]),
    Template("weekly_monday", "@weekly", "Once a week on Sunday midnight", "weekly", ["weekly"]),
    Template("monthly_first", "@monthly", "First day of each month", "monthly", ["monthly"]),
    Template("monthly_last", "0 0 28-31 * *", "Approx. last days of month", "monthly", ["monthly"]),
    Template("yearly", "@yearly", "Once a year on Jan 1st", "yearly", ["yearly"]),
    Template("weekends", "0 10 * * 6,0", "Weekends at 10 AM", "weekly", ["weekend"]),
]


def list_templates(category: Optional[str] = None) -> List[Template]:
    """Return all templates, optionally filtered by category."""
    if category is None:
        return list(_TEMPLATES)
    return [t for t in _TEMPLATES if t.category == category]


def find_by_name(name: str) -> Optional[Template]:
    """Look up a template by its name. Returns None if not found."""
    for t in _TEMPLATES:
        if t.name == name:
            return t
    return None


def find_by_tag(tag: str) -> List[Template]:
    """Return templates that include the given tag."""
    return [t for t in _TEMPLATES if tag in t.tags]


def categories() -> List[str]:
    """Return a sorted list of unique category names."""
    return sorted({t.category for t in _TEMPLATES})


def format_table(templates: Optional[List[Template]] = None) -> str:
    """Render a simple text table of templates."""
    rows = templates if templates is not None else _TEMPLATES
    if not rows:
        return "No templates found."
    col_name = max(len(t.name) for t in rows)
    col_expr = max(len(t.expression) for t in rows)
    header = f"{'NAME':<{col_name}}  {'EXPRESSION':<{col_expr}}  DESCRIPTION"
    sep = "-" * len(header)
    lines = [header, sep]
    for t in rows:
        lines.append(f"{t.name:<{col_name}}  {t.expression:<{col_expr}}  {t.description}")
    return "\n".join(lines)
