"""Command-line interface for crontab-viz."""

import argparse
import sys
from datetime import datetime

from .parser import parse, ParseError
from .timeline import render_timeline


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="crontab-viz",
        description="Parse a crontab expression and display its upcoming schedule.",
    )
    p.add_argument(
        "expression",
        help='Crontab expression in quotes, e.g. "*/5 * * * *"',
    )
    p.add_argument(
        "-n", "--count",
        type=int,
        default=10,
        metavar="N",
        help="Number of upcoming occurrences to show (default: 10)",
    )
    p.add_argument(
        "--from",
        dest="from_time",
        default=None,
        metavar="DATETIME",
        help="Start datetime in ISO format YYYY-MM-DDTHH:MM (default: now)",
    )
    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.from_time:
        try:
            start = datetime.fromisoformat(args.from_time)
        except ValueError:
            print(
                f"Error: invalid datetime format '{args.from_time}'. "
                "Use YYYY-MM-DDTHH:MM.",
                file=sys.stderr,
            )
            return 2
    else:
        start = datetime.now()

    try:
        expr = parse(args.expression)
    except ParseError as exc:
        print(f"Parse error: {exc}", file=sys.stderr)
        return 1

    output = render_timeline(expr, start, count=args.count)
    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
