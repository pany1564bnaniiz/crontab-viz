"""Persist and retrieve tagged cron expressions using a JSON file store."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from .parser import parse
from .tags import TaggedExpression, tag_expression

_DEFAULT_PATH = Path.home() / ".crontab_viz" / "tags.json"


def _load(path: Path) -> List[Dict]:
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _save(records: List[Dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(records, indent=2), encoding="utf-8")


def save_tagged(
    expression: str,
    user_tags: Optional[List[str]] = None,
    path: Path = _DEFAULT_PATH,
) -> TaggedExpression:
    """Parse, auto-tag, merge user tags, and persist the tagged expression."""
    parsed = parse(expression)
    te = tag_expression(expression, parsed, user_tags=user_tags)

    records = _load(path)
    # Update existing entry or append new one
    for rec in records:
        if rec.get("expression") == expression:
            existing = set(rec.get("user_tags", []))
            existing.update(te.user_tags)
            rec["user_tags"] = sorted(existing)
            break
    else:
        records.append({"expression": expression, "user_tags": te.user_tags})

    _save(records, path)
    return te


def load_tagged(path: Path = _DEFAULT_PATH) -> List[TaggedExpression]:
    """Load all persisted tagged expressions from disk."""
    results = []
    for rec in _load(path):
        expr_str = rec.get("expression", "")
        user_tags = rec.get("user_tags", [])
        try:
            parsed = parse(expr_str)
            results.append(tag_expression(expr_str, parsed, user_tags=user_tags))
        except Exception:
            pass
    return results


def remove_tag(
    expression: str,
    tag: str,
    path: Path = _DEFAULT_PATH,
) -> bool:
    """Remove a user tag from a stored expression. Returns True if found."""
    records = _load(path)
    changed = False
    for rec in records:
        if rec.get("expression") == expression:
            before = set(rec.get("user_tags", []))
            after = before - {tag.lower().strip()}
            if before != after:
                rec["user_tags"] = sorted(after)
                changed = True
            break
    if changed:
        _save(records, path)
    return changed
