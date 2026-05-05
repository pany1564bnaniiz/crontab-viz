"""Tag and categorize cron expressions for organization and filtering."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .parser import CronExpression

# Built-in category tags derived from expression patterns
_BUILTIN_TAGS = {
    "every-minute": lambda e: e.minute == list(range(60)),
    "hourly": lambda e: e.minute != list(range(60)) and e.hour == list(range(24)),
    "daily": lambda e: e.hour != list(range(24)) and e.dom == list(range(1, 32)),
    "weekly": lambda e: e.dow != list(range(7)),
    "monthly": lambda e: e.dom != list(range(1, 32)) and e.month == list(range(1, 13)),
}


@dataclass
class TaggedExpression:
    expression: str
    auto_tags: List[str] = field(default_factory=list)
    user_tags: List[str] = field(default_factory=list)

    @property
    def all_tags(self) -> List[str]:
        return sorted(set(self.auto_tags + self.user_tags))

    def has_tag(self, tag: str) -> bool:
        return tag in self.all_tags


def auto_tag(expr: CronExpression) -> List[str]:
    """Return a list of built-in category tags that match the expression."""
    tags = []
    for tag_name, predicate in _BUILTIN_TAGS.items():
        try:
            if predicate(expr):
                tags.append(tag_name)
        except Exception:
            pass
    return tags


def tag_expression(
    expression: str,
    parsed: CronExpression,
    user_tags: Optional[List[str]] = None,
) -> TaggedExpression:
    """Create a TaggedExpression with auto-detected and optional user tags."""
    return TaggedExpression(
        expression=expression,
        auto_tags=auto_tag(parsed),
        user_tags=[t.lower().strip() for t in (user_tags or [])],
    )


def filter_by_tag(items: List[TaggedExpression], tag: str) -> List[TaggedExpression]:
    """Return only those TaggedExpressions that carry the given tag."""
    return [item for item in items if item.has_tag(tag)]


def all_tags(items: List[TaggedExpression]) -> List[str]:
    """Return a sorted, deduplicated list of every tag across all items."""
    seen: set = set()
    for item in items:
        seen.update(item.all_tags)
    return sorted(seen)
