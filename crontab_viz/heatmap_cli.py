"""CLI entry-point for the heatmap subcommand."""
from __future__ import annotations

import argparse
import sys

from .heatmap import build_heatmap, render_heatmap
from .validator import validate


def build_parser(parent: argparse.ArgumentParser | None = None) -> argparse.ArgumentParser:
    if parent is None:
        parser = argparse.ArgumentParser(
            prog="crontab-heatmap",
            description="Render an hour × weekday heatmap for a cron expression.",
        )
    else:
        parser = parent

    parser.add_argument("expression", help="Cron expression (quote it!)")
    parser.add_argument(
        "--weeks",
        type=int,
        default=4,
        metavar="N",
        help="Number of weeks to simulate (default: 4)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable ANSI colour output",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.no_color:
        from . import colors
        colors.disable()

    result = validate(args.expression)
    if not result:
        print(f"Error: {'; '.join(result.errors)}", file=sys.stderr)
        return 1

    if result.warnings:
        for w in result.warnings:
            print(f"Warning: {w}", file=sys.stderr)

    if args.weeks < 1 or args.weeks > 52:
        print("Error: --weeks must be between 1 and 52.", file=sys.stderr)
        return 1

    try:
        data = build_heatmap(args.expression, weeks=args.weeks)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(render_heatmap(data))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
