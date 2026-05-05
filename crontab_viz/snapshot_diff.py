"""Compare two snapshots to surface schedule changes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Set

from crontab_viz.snapshot import Snapshot


@dataclass
class SnapshotDiffResult:
    added: List[str]       # occurrences in new but not old
    removed: List[str]     # occurrences in old but not new
    expression_changed: bool
    description_changed: bool
    old_expression: str
    new_expression: str
    old_description: str
    new_description: str

    @property
    def has_changes(self) -> bool:
        return bool(
            self.added
            or self.removed
            or self.expression_changed
            or self.description_changed
        )

    def summary(self) -> str:
        if not self.has_changes:
            return "No changes between snapshots."
        lines: List[str] = []
        if self.expression_changed:
            lines.append(
                f"Expression: '{self.old_expression}' → '{self.new_expression}'"
            )
        if self.description_changed:
            lines.append(
                f"Description changed: '{self.old_description}' → '{self.new_description}'"
            )
        if self.added:
            lines.append(f"+{len(self.added)} new occurrence(s)")
        if self.removed:
            lines.append(f"-{len(self.removed)} removed occurrence(s)")
        return "\n".join(lines)


def diff_snapshots(old: Snapshot, new: Snapshot) -> SnapshotDiffResult:
    """Diff two snapshots and return a structured result."""
    old_set: Set[str] = set(old.occurrences)
    new_set: Set[str] = set(new.occurrences)

    return SnapshotDiffResult(
        added=sorted(new_set - old_set),
        removed=sorted(old_set - new_set),
        expression_changed=old.expression != new.expression,
        description_changed=old.description != new.description,
        old_expression=old.expression,
        new_expression=new.expression,
        old_description=old.description,
        new_description=new.description,
    )
