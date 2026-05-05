"""CLI entry point for crontab-viz."""

import argparse
import sys

from .parser import parse, ParseError
from .timeline import render_timeline
from .formatter import describe
from .validator import validate
from .export import export
from .diff import diff
from .history import record
from .interactive import print_history, pick_from_history


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="crontab-viz",
        description="Parse and visualise crontab expressions.",
    )
    sub = p.add_subparsers(dest="command")

    show = sub.add_parser("show", help="Show timeline for an expression")
    show.add_argument("expression", nargs="+", help="Cron expression (quoted)")
    show.add_argument("-n", "--count", type=int, default=10, help="Number of occurrences")
    show.add_argument("--no-color", action="store_true")

    desc = sub.add_parser("describe", help="Human-readable description")
    desc.add_argument("expression", nargs="+")

    val = sub.add_parser("validate", help="Validate a cron expression")
    val.add_argument("expression", nargs="+")

    exp = sub.add_parser("export", help="Export occurrences to JSON or CSV")
    exp.add_argument("expression", nargs="+")
    exp.add_argument("-f", "--format", choices=["json", "csv"], default="json")
    exp.add_argument("-n", "--count", type=int, default=10)

    dif = sub.add_parser("diff", help="Compare two cron expressions")
    dif.add_argument("expression_a")
    dif.add_argument("expression_b")

    sub.add_parser("history", help="Show previously used expressions")

    pick = sub.add_parser("pick", help="Interactively pick from history")
    pick.add_argument("-n", "--count", type=int, default=10)

    return p


def _join(parts):
    return " ".join(parts)


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "show":
        expr = _join(args.expression)
        try:
            cron = parse(expr)
        except ParseError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        record(expr)
        print(render_timeline(cron, count=args.count))

    elif args.command == "describe":
        expr = _join(args.expression)
        try:
            cron = parse(expr)
        except ParseError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        record(expr)
        print(describe(cron))

    elif args.command == "validate":
        expr = _join(args.expression)
        result = validate(expr)
        if result:
            print("Valid expression.")
            if result.warnings:
                for w in result.warnings:
                    print(f"Warning: {w}")
        else:
            for e in result.errors:
                print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "export":
        expr = _join(args.expression)
        try:
            cron = parse(expr)
        except ParseError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        record(expr)
        print(export(cron, fmt=args.format, count=args.count))

    elif args.command == "diff":
        try:
            result = diff(args.expression_a, args.expression_b)
        except ParseError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        print(result.summary())
        sys.exit(0 if result.same else 1)

    elif args.command == "history":
        print_history()

    elif args.command == "pick":
        expr = pick_from_history()
        if expr:
            cron = parse(expr)
            print(render_timeline(cron, count=args.count))

    else:
        parser.print_help()
