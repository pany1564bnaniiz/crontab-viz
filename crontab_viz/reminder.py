"""Reminder module: attach notes/reminders to cron expressions and persist them."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

DEFAULT_PATH = os.path.join(os.path.expanduser("~"), ".crontab_viz_reminders.json")


@dataclass
class Reminder:
    expression: str
    note: str
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "expression": self.expression,
            "note": self.note,
            "created_at": self.created_at,
            "tags": self.tags,
        }

    @staticmethod
    def from_dict(d: dict) -> "Reminder":
        return Reminder(
            expression=d["expression"],
            note=d["note"],
            created_at=d.get("created_at", ""),
            tags=d.get("tags", []),
        )


def _load(path: str) -> List[dict]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _save(records: List[dict], path: str) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(records, fh, indent=2)


def add_reminder(expression: str, note: str, tags: Optional[List[str]] = None,
                 path: str = DEFAULT_PATH) -> Reminder:
    """Persist a new reminder for *expression* with *note*."""
    reminder = Reminder(expression=expression, note=note, tags=tags or [])
    records = _load(path)
    records.append(reminder.to_dict())
    _save(records, path)
    return reminder


def load_reminders(expression: Optional[str] = None,
                   path: str = DEFAULT_PATH) -> List[Reminder]:
    """Return all reminders, optionally filtered by *expression*."""
    records = _load(path)
    reminders = [Reminder.from_dict(r) for r in records]
    if expression is not None:
        reminders = [r for r in reminders if r.expression == expression]
    return reminders


def remove_reminder(expression: str, note: str,
                    path: str = DEFAULT_PATH) -> bool:
    """Remove the first reminder matching *expression* and *note*. Returns True if removed."""
    records = _load(path)
    original_len = len(records)
    records = [
        r for r in records
        if not (r["expression"] == expression and r["note"] == note)
    ]
    if len(records) == original_len:
        return False
    _save(records, path)
    return True


def clear_reminders(path: str = DEFAULT_PATH) -> None:
    """Delete all stored reminders."""
    _save([], path)
