"""CLI entry-point for the calendar view feature."""
from __future__ import annotations

import argparse
import sys
from datetime import datetime

from .calendar_view import build_calendar, render_calendar
from .parser import ParseError
from .colors import disable as disable_colors

__all__ = ["build_parser", "main"]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="crontab-calendar",
        description="Render a monthly calendar highlighting cron fire days.",
    )
    p.add_argument("expression", help="Cron expression (quote if it contains spaces)")
    p.add_argument(
        "--year",
        type=int,
        default=None,
        help="Year to display (default: current year)",
    )
    p.add_argument(
        "--month",
        type=int,
        default=None,
        choices=range(1, 13),
        metavar="MONTH",
        help="Month to display 1-12 (default: current month)",
    )
    p.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI color output",
    )
    p.add_argument(
        "--lookahead",
        type=int,
        default=1500,
        help="Max occurrences to scan when building calendar (default: 1500)",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.no_color:
        disable_colors()

    now = datetime.now()
    year = args.year or now.year
    month = args.month or now.month

    if not (1 <= month <= 12):
        parser.error(f"Month must be between 1 and 12, got {month}")

    try:
        view = build_calendar(
            args.expression,
            year=year,
            month=month,
            lookahead=args.lookahead,
        )
    except ParseError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(render_calendar(view))
    fire_count = len(view.fire_days)
    label = "day" if fire_count == 1 else "days"
    print(f"\n  Fires on {fire_count} {label} this month.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
