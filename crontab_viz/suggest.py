"""Suggests cron expressions based on natural-language-like descriptions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Suggestion:
    expression: str
    label: str
    description: str


_BUILTIN: List[Suggestion] = [
    Suggestion("* * * * *",   "every minute",          "Runs once every minute."),
    Suggestion("0 * * * *",   "every hour",            "Runs at the start of every hour."),
    Suggestion("0 0 * * *",   "every day at midnight", "Runs daily at 00:00."),
    Suggestion("0 12 * * *",  "every day at noon",     "Runs daily at 12:00."),
    Suggestion("0 0 * * 0",   "every sunday",          "Runs at midnight every Sunday."),
    Suggestion("0 0 1 * *",   "first of month",        "Runs at midnight on the 1st of each month."),
    Suggestion("0 0 1 1 *",   "yearly",                "Runs once a year on 1 Jan at midnight."),
    Suggestion("*/5 * * * *", "every 5 minutes",       "Runs every 5 minutes."),
    Suggestion("*/15 * * * *","every 15 minutes",      "Runs every 15 minutes."),
    Suggestion("*/30 * * * *","every 30 minutes",      "Runs every 30 minutes."),
    Suggestion("0 9-17 * * 1-5", "business hours",    "Runs hourly during business hours (Mon-Fri 09:00-17:00)."),
    Suggestion("0 0 * * 1-5", "weekdays at midnight",  "Runs at midnight on weekdays only."),
    Suggestion("@reboot",     "at reboot",             "Runs once when the system starts."),
]


def _score(suggestion: Suggestion, query: str) -> int:
    """Return a relevance score (higher is better); 0 means no match."""
    q = query.lower()
    label = suggestion.label.lower()
    desc  = suggestion.description.lower()
    expr  = suggestion.expression.lower()

    if q == expr:
        return 100
    if q == label:
        return 90
    tokens = q.split()
    hits = sum(1 for t in tokens if t in label or t in desc or t in expr)
    return hits * 10 if hits else 0


def suggest(query: str, top_n: int = 5) -> List[Suggestion]:
    """Return up to *top_n* suggestions whose label/description matches *query*.

    If *query* is empty or ``"*"`` all built-in suggestions are returned
    (up to *top_n*).
    """
    if not query or query.strip() == "*":
        return _BUILTIN[:top_n]

    scored = [(s, _score(s, query.strip())) for s in _BUILTIN]
    scored = [(s, sc) for s, sc in scored if sc > 0]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [s for s, _ in scored[:top_n]]


def format_suggestions(suggestions: List[Suggestion], *, color: bool = True) -> str:
    """Render a list of suggestions as a human-readable string."""
    if not suggestions:
        return "No suggestions found."

    try:
        from crontab_viz.colors import bold, dim, cyan  # type: ignore
    except Exception:  # pragma: no cover
        bold = dim = cyan = lambda x: x  # type: ignore

    lines = [bold("Suggestions:")]
    for s in suggestions:
        lines.append(f"  {cyan(s.expression):<22}  {s.label}")
        lines.append(f"  {dim(s.description)}")
    return "\n".join(lines)
