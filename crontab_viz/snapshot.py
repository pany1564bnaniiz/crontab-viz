"""Snapshot: save and compare crontab schedule states over time."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

DEFAULT_SNAPSHOT_FILE = os.path.join(
    os.path.expanduser("~"), ".crontab_viz_snapshots.json"
)


@dataclass
class Snapshot:
    expression: str
    description: str
    occurrences: List[str]
    taken_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    label: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "expression": self.expression,
            "description": self.description,
            "occurrences": self.occurrences,
            "taken_at": self.taken_at,
            "label": self.label,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Snapshot":
        return cls(
            expression=data["expression"],
            description=data["description"],
            occurrences=data["occurrences"],
            taken_at=data["taken_at"],
            label=data.get("label"),
        )


def _load(path: str) -> List[dict]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _save(records: List[dict], path: str) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(records, fh, indent=2)


def take_snapshot(
    snapshot: Snapshot,
    path: str = DEFAULT_SNAPSHOT_FILE,
) -> None:
    """Persist a snapshot to disk."""
    records = _load(path)
    records.append(snapshot.to_dict())
    _save(records, path)


def load_snapshots(path: str = DEFAULT_SNAPSHOT_FILE) -> List[Snapshot]:
    """Return all stored snapshots."""
    return [Snapshot.from_dict(r) for r in _load(path)]


def clear_snapshots(path: str = DEFAULT_SNAPSHOT_FILE) -> None:
    """Delete all stored snapshots."""
    _save([], path)


def find_by_label(
    label: str, path: str = DEFAULT_SNAPSHOT_FILE
) -> Optional[Snapshot]:
    """Return the most recent snapshot with the given label, or None."""
    matches = [s for s in load_snapshots(path) if s.label == label]
    return matches[-1] if matches else None
