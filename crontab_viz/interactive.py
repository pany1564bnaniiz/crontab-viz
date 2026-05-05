"""Interactive history browser for the CLI."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from crontab_viz.colors import bold, dim, green
from crontab_viz.history import load_history, recent_expressions


def _render_history_table(entries: List[dict]) -> str:
    """Return a formatted table of history entries."""
    if not entries:
        return dim("  (no history recorded yet)")

    lines: List[str] = [bold("  # │ Recorded at          │ Expression")]
    lines.append(dim("  ──┼──────────────────────┼────────────────────────────"))
    for idx, entry in enumerate(entries, start=1):
        num = str(idx).rjust(3)
        ts = entry.get("recorded_at", "unknown")[:19].replace("T", " ")
        expr = entry.get("expression", "")
        lines.append(f"  {dim(num)} │ {ts} │ {green(expr)}")
    return "\n".join(lines)


def print_history(
    n: int = 20,
    path: Optional[Path] = None,
) -> None:
    """Print the *n* most recent history entries to stdout."""
    entries = load_history(path)[:n]
    print(bold("\nRecent crontab expressions:\n"))
    print(_render_history_table(entries))
    print()


def pick_from_history(
    n: int = 20,
    path: Optional[Path] = None,
) -> Optional[str]:
    """Interactively select an expression from history.

    Returns the chosen expression string, or ``None`` if the user cancels.
    """
    entries = load_history(path)[:n]
    if not entries:
        print(dim("No history available."))
        return None

    print_history(n=n, path=path)
    try:
        raw = input(bold("Enter number to reuse (or blank to cancel): ")).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return None

    if not raw:
        return None

    try:
        choice = int(raw)
    except ValueError:
        print(dim("Invalid selection."))
        return None

    if 1 <= choice <= len(entries):
        return entries[choice - 1]["expression"]

    print(dim(f"Selection out of range (1–{len(entries)})."))
    return None
