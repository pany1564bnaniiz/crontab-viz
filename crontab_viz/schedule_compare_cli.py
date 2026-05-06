"""CLI entry-point for schedule comparison."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime

from .schedule_compare import compare_schedules
from .colors import bold, green, yellow, red, dim


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="crontab-compare",
        description="Compare two cron schedule timelines.",
    )
    p.add_argument("expr_a", help="First cron expression (quote it)")
    p.add_argument("expr_b", help="Second cron expression (quote it)")
    p.add_argument(
        "-n", "--count", type=int, default=20, help="Number of occurrences to compare"
    )
    p.add_argument(
        "--no-color", action="store_true", help="Disable colored output"
    )
    return p


def _fmt_dt(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M")


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.no_color:
        from . import colors
        colors.disable()

    try:
        result = compare_schedules(args.expr_a, args.expr_b, count=args.count)
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(bold("=== Schedule Comparison ==="))
    print(result.summary())
    print()

    if result.common:
        print(bold(green(f"Shared occurrences ({len(result.common)}):")), dim("(both A and B)"))
        for dt in result.common:
            print(f"  {green(_fmt_dt(dt))}")
        print()

    if result.only_in_a:
        print(bold(yellow(f"Only in A ({len(result.only_in_a)}):")), dim(args.expr_a))
        for dt in result.only_in_a:
            print(f"  {yellow(_fmt_dt(dt))}")
        print()

    if result.only_in_b:
        print(bold(red(f"Only in B ({len(result.only_in_b)}):")), dim(args.expr_b))
        for dt in result.only_in_b:
            print(f"  {red(_fmt_dt(dt))}")


if __name__ == "__main__":
    main()
