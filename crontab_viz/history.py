"""Track and persist recently used crontab expressions."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

DEFAULT_HISTORY_PATH = Path.home() / ".crontab_viz_history.json"
MAX_HISTORY = 50


def _load(path: Path) -> List[dict]:
    """Load history entries from disk."""
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, list):
            return data
    except (json.JSONDecodeError, OSError):
        pass
    return []


def _save(entries: List[dict], path: Path) -> None:
    """Persist history entries to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(entries, fh, indent=2)


def record(
    expression: str,
    path: Optional[Path] = None,
) -> None:
    """Add *expression* to history, deduplicating and capping at MAX_HISTORY."""
    history_path = path or DEFAULT_HISTORY_PATH
    entries = _load(history_path)

    # Remove previous occurrence of the same expression
    entries = [e for e in entries if e.get("expression") != expression]

    entries.insert(
        0,
        {
            "expression": expression,
            "recorded_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        },
    )

    _save(entries[:MAX_HISTORY], history_path)


def load_history(path: Optional[Path] = None) -> List[dict]:
    """Return all history entries, newest first."""
    return _load(path or DEFAULT_HISTORY_PATH)


def clear(path: Optional[Path] = None) -> None:
    """Remove all history entries."""
    history_path = path or DEFAULT_HISTORY_PATH
    _save([], history_path)


def recent_expressions(n: int = 10, path: Optional[Path] = None) -> List[str]:
    """Return the *n* most recently used expression strings."""
    return [e["expression"] for e in load_history(path)[:n]]
