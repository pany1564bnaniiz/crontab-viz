"""CLI entry-point for the next-N-runs feature."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime

from .next_n import compute, format_next_n, compare_next_n
from .colors import bold, error as color_error


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="crontab-next",
        description="Show the next N scheduled run times for cron expression(s).",
    )
    p.add_argument(
        "expressions",
        nargs="+",
        metavar="EXPR",
        help="One or more cron expressions (quote each one).",
    )
    p.add_argument(
        "-n",
        "--count",
        type=int,
        default=5,
        metavar="N",
        help="Number of future occurrences to display (default: 5, max: 100).",
    )
    p.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable ANSI color output.",
    )
    return p


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.no_color:
        from . import colors
        colors.disable()

    now = datetime.utcnow()
    results = compare_next_n(args.expressions, count=args.count, now=now)

    exit_code = 0
    for result in results:
        if not result.ok:
            print(color_error(f"Error: {result.error}"), file=sys.stderr)
            exit_code = 1
            continue
        print(bold(format_next_n(result, now=now)))
        print()

    sys.exit(exit_code)


if __name__ == "__main__":  # pragma: no cover
    main()
