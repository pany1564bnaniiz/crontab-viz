"""CLI entry-point for burst detection."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime

from .burst import detect_bursts
from .colors import bold, yellow, red, green, dim


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="crontab-burst",
        description="Detect burst windows in a cron schedule.",
    )
    p.add_argument("expression", help="Cron expression (quote it)")
    p.add_argument(
        "--window",
        type=int,
        default=3600,
        metavar="SECONDS",
        help="Rolling window size in seconds (default: 3600)",
    )
    p.add_argument(
        "--threshold",
        type=int,
        default=10,
        metavar="N",
        help="Minimum fires within window to flag as burst (default: 10)",
    )
    p.add_argument(
        "--lookahead",
        type=int,
        default=500,
        metavar="N",
        help="Number of future occurrences to examine (default: 500)",
    )
    p.add_argument(
        "--top",
        type=int,
        default=5,
        metavar="N",
        help="Show at most N burst windows (default: 5)",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    result = detect_bursts(
        args.expression,
        window_seconds=args.window,
        threshold=args.threshold,
        lookahead=args.lookahead,
    )

    if not result.ok():
        print(red(f"Error: {result.error}"), file=sys.stderr)
        return 1

    print(bold(f"Burst analysis: {args.expression}"))
    print(dim(f"Window: {args.window}s  |  Threshold: {args.threshold} fires"))
    print()

    if not result.bursts:
        print(green("No burst windows detected."))
        return 0

    print(yellow(result.summary()))
    print()
    for bw in result.bursts[: args.top]:
        fmt = "%Y-%m-%d %H:%M"
        print(
            f"  {bold(bw.start.strftime(fmt))} – {bw.end.strftime(fmt)}  "
            f"{yellow(str(bw.count) + ' fires')}"
        )
    if len(result.bursts) > args.top:
        print(dim(f"  … and {len(result.bursts) - args.top} more window(s)."))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
