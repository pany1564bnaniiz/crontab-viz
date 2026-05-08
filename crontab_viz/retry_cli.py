"""CLI entry-point for retry policy analysis."""
from __future__ import annotations

import argparse
import sys
from datetime import datetime

from .retry import analyze_retry
from .colors import bold, green, red, yellow


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="crontab-retry",
        description="Analyse whether retry attempts overlap with scheduled runs.",
    )
    p.add_argument("expression", help="Cron expression (quote it)")
    p.add_argument(
        "-i", "--interval",
        type=int,
        default=5,
        metavar="MINUTES",
        help="Minutes between retry attempts (default: 5)",
    )
    p.add_argument(
        "-r", "--retries",
        type=int,
        default=3,
        metavar="N",
        help="Maximum number of retries (default: 3)",
    )
    p.add_argument(
        "-w", "--window",
        type=int,
        default=24,
        metavar="RUNS",
        help="Number of upcoming runs to inspect (default: 24)",
    )
    p.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colour output",
    )
    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.no_color:
        from . import colors
        colors.disable()

    result = analyze_retry(
        expression=args.expression,
        retry_interval_minutes=args.interval,
        max_retries=args.retries,
        window=args.window,
        now=datetime.utcnow(),
    )

    if not result.ok:
        print(red(f"Error: {result.error}"), file=sys.stderr)
        return 1

    if result.has_conflicts:
        print(bold(yellow("⚠ Retry conflicts detected:")))
        for c in result.conflicts:
            print(f"  {red('•')} {c}")
    else:
        print(
            green("✓") + " " +
            bold("No conflicts") +
            f" — interval={args.interval}m, retries={args.retries}, "
            f"window={args.window} runs"
        )

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
