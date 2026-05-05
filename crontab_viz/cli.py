"""Command-line interface for crontab-viz."""

import argparse
import sys
from datetime import datetime

from .parser import parse, ParseError
from .timeline import next_occurrences, render_timeline
from .formatter import describe
from .export import export
from .validator import validate


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="crontab-viz",
        description="Parse and visualise crontab expressions.",
    )
    p.add_argument("expression", nargs="?", help="Crontab expression (quoted).")
    p.add_argument(
        "-n", "--count",
        type=int, default=10,
        metavar="N",
        help="Number of upcoming occurrences to show (default: 10).",
    )
    p.add_argument(
        "--from",
        dest="start",
        default=None,
        metavar="YYYY-MM-DDTHH:MM",
        help="Start datetime for timeline (default: now).",
    )
    p.add_argument(
        "--format",
        dest="fmt",
        choices=["timeline", "json", "csv"],
        default="timeline",
        help="Output format (default: timeline).",
    )
    p.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI colour output.",
    )
    p.add_argument(
        "--validate",
        action="store_true",
        help="Validate the expression and exit without rendering.",
    )
    return p


def main(argv=None) -> int:  # noqa: C901
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.expression is None:
        parser.print_help()
        return 0

    if args.no_color:
        from . import colors
        colors.disable()

    # --- validate mode ---
    if args.validate:
        result = validate(args.expression)
        if result.valid:
            print("✓ Expression is valid.")
            for w in result.warnings:
                print(f"  warning: {w}", file=sys.stderr)
            return 0
        else:
            print("✗ Expression is invalid:", file=sys.stderr)
            for e in result.errors:
                print(f"  {e}", file=sys.stderr)
            return 1

    try:
        cron = parse(args.expression)
    except ParseError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    start = datetime.now()
    if args.start:
        try:
            start = datetime.fromisoformat(args.start)
        except ValueError:
            print(f"Error: invalid --from datetime '{args.start}'", file=sys.stderr)
            return 1

    occurrences = next_occurrences(cron, count=args.count, start=start)

    if args.fmt == "timeline":
        print(describe(cron))
        print(render_timeline(occurrences, start=start))
    else:
        print(export(occurrences, fmt=args.fmt, expression=args.expression))

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
