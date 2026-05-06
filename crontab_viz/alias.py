"""Cron expression alias registry: resolve, register, and list named aliases."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

# Built-in aliases mirroring common cron implementations
_BUILTIN: Dict[str, str] = {
    "@yearly": "0 0 1 1 *",
    "@annually": "0 0 1 1 *",
    "@monthly": "0 0 1 * *",
    "@weekly": "0 0 * * 0",
    "@daily": "0 0 * * *",
    "@midnight": "0 0 * * *",
    "@hourly": "0 * * * *",
    "@reboot": None,  # special – not a time-based expression
}

# User-registered aliases (runtime only; use alias_store for persistence)
_custom: Dict[str, str] = {}


@dataclass
class AliasEntry:
    name: str
    expression: Optional[str]  # None for special aliases like @reboot
    builtin: bool


def resolve(alias: str) -> Optional[str]:
    """Return the cron expression for *alias*, or None if not found / special."""
    key = alias.lower()
    if key in _custom:
        return _custom[key]
    return _BUILTIN.get(key)


def register(name: str, expression: str) -> None:
    """Register a custom alias at runtime.

    Raises ValueError if *name* conflicts with a built-in alias.
    """
    key = name.lower()
    if key in _BUILTIN:
        raise ValueError(f"Cannot override built-in alias '{key}'")
    if not name.startswith("@"):
        raise ValueError("Alias names must start with '@'")
    _custom[key] = expression


def unregister(name: str) -> bool:
    """Remove a custom alias. Returns True if it existed."""
    return _custom.pop(name.lower(), None) is not None


def list_aliases(include_special: bool = False) -> List[AliasEntry]:
    """Return all known aliases as AliasEntry objects.

    Args:
        include_special: When False, aliases with no expression (e.g. @reboot)
                         are excluded.
    """
    entries: List[AliasEntry] = []
    for name, expr in _BUILTIN.items():
        if expr is None and not include_special:
            continue
        entries.append(AliasEntry(name=name, expression=expr, builtin=True))
    for name, expr in _custom.items():
        entries.append(AliasEntry(name=name, expression=expr, builtin=False))
    return sorted(entries, key=lambda e: e.name)


def is_alias(token: str) -> bool:
    """Return True if *token* is a known alias name."""
    return token.lower() in _BUILTIN or token.lower() in _custom
