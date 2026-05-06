"""Generate a formatted report of all reminders, optionally grouped by tag."""
from __future__ import annotations

from collections import defaultdict
from typing import List, Optional

from crontab_viz.reminder import Reminder, load_reminders
from crontab_viz.colors import bold, dim, cyan
from crontab_viz.formatter import describe
from crontab_viz.parser import parse


def _safe_describe(expression: str) -> str:
    try:
        return describe(parse(expression))
    except Exception:
        return "(unable to describe)"


def report_by_tag(reminders: List[Reminder]) -> str:
    """Return a multi-line string grouping reminders by tag."""
    groups: dict[str, List[Reminder]] = defaultdict(list)
    untagged: List[Reminder] = []
    for r in reminders:
        if r.tags:
            for tag in r.tags:
                groups[tag].append(r)
        else:
            untagged.append(r)

    lines: List[str] = []
    for tag in sorted(groups):
        lines.append(bold(f"[{tag}]"))
        for r in groups[tag]:
            lines.append(f"  {cyan(r.expression)}  {_safe_describe(r.expression)}")
            lines.append(f"    {r.note}")
            lines.append(dim(f"    Added: {r.created_at}"))
    if untagged:
        lines.append(bold("[untagged]"))
        for r in untagged:
            lines.append(f"  {cyan(r.expression)}  {_safe_describe(r.expression)}")
            lines.append(f"    {r.note}")
    return "\n".join(lines)


def report_flat(reminders: List[Reminder]) -> str:
    """Return a flat list report of all reminders."""
    if not reminders:
        return dim("No reminders stored.")
    lines: List[str] = [bold(f"Reminders ({len(reminders)})"), ""]
    for i, r in enumerate(reminders, 1):
        tags_str = f" [{', '.join(r.tags)}]" if r.tags else ""
        lines.append(f"{i}. {bold(r.expression)}{tags_str}")
        lines.append(f"   Schedule : {_safe_describe(r.expression)}")
        lines.append(f"   Note     : {r.note}")
        lines.append(dim(f"   Created  : {r.created_at}"))
        lines.append("")
    return "\n".join(lines)


def generate_report(grouped: bool = False,
                    expression: Optional[str] = None,
                    path: Optional[str] = None) -> str:
    """Load reminders and return a formatted report string."""
    kwargs = {} if path is None else {"path": path}
    reminders = load_reminders(expression=expression, **kwargs)
    if grouped:
        return report_by_tag(reminders)
    return report_flat(reminders)
