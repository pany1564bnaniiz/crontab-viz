"""CLI interface for managing cron expression reminders."""
from __future__ import annotations

import argparse
import sys
from typing import List

from crontab_viz.reminder import add_reminder, load_reminders, remove_reminder, clear_reminders
from crontab_viz.validator import validate
from crontab_viz.colors import bold, dim, green, red


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-reminder",
        description="Attach notes/reminders to cron expressions.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    add_p = sub.add_parser("add", help="Add a reminder")
    add_p.add_argument("expression", help="Cron expression (quoted)")
    add_p.add_argument("note", help="Reminder note text")
    add_p.add_argument("--tags", nargs="*", default=[], metavar="TAG")

    list_p = sub.add_parser("list", help="List reminders")
    list_p.add_argument("--expression", default=None, help="Filter by expression")

    rm_p = sub.add_parser("remove", help="Remove a reminder")
    rm_p.add_argument("expression")
    rm_p.add_argument("note")

    sub.add_parser("clear", help="Clear all reminders")
    return parser


def _cmd_add(args: argparse.Namespace) -> int:
    result = validate(args.expression)
    if not result:
        print(red(f"Invalid expression: {'; '.join(result.errors)}"), file=sys.stderr)
        return 1
    reminder = add_reminder(args.expression, args.note, tags=args.tags)
    print(green("Reminder added:"), bold(reminder.expression))
    print(dim(f"  Note: {reminder.note}"))
    if reminder.tags:
        print(dim(f"  Tags: {', '.join(reminder.tags)}"))
    return 0


def _cmd_list(args: argparse.Namespace) -> int:
    reminders = load_reminders(expression=args.expression)
    if not reminders:
        print(dim("No reminders found."))
        return 0
    for r in reminders:
        tags_str = f" [{', '.join(r.tags)}]" if r.tags else ""
        print(f"{bold(r.expression)}{tags_str}")
        print(f"  {r.note}")
        print(dim(f"  Created: {r.created_at}"))
    return 0


def _cmd_remove(args: argparse.Namespace) -> int:
    removed = remove_reminder(args.expression, args.note)
    if removed:
        print(green("Reminder removed."))
    else:
        print(red("No matching reminder found."), file=sys.stderr)
        return 1
    return 0


def main(argv: List[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    dispatch = {
        "add": _cmd_add,
        "list": _cmd_list,
        "remove": _cmd_remove,
        "clear": lambda _: (clear_reminders(), print(green("All reminders cleared."))) and 0 or 0,
    }
    code = dispatch[args.command](args)
    sys.exit(code or 0)


if __name__ == "__main__":
    main()
