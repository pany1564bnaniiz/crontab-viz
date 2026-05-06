"""CLI for annotating cron expressions with human-readable comments."""

from __future__ import annotations

import argparse
import sys

from .annotate import annotate, annotate_many
from .colors import bold, yellow, red, green, dim


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="crontab-annotate",
        description="Annotate cron expressions with human-readable descriptions.",
    )
    p.add_argument("expression", nargs="*", help="Cron expression(s) to annotate")
    p.add_argument(
        "--inline",
        action="store_true",
        default=False,
        help="Output expression with trailing inline comment only",
    )
    p.add_argument(
        "--comment-style",
        default="#",
        metavar="CHAR",
        help="Comment prefix for inline mode (default: #)",
    )
    p.add_argument(
        "--file",
        metavar="PATH",
        help="Read expressions from a file (one per line)",
    )
    return p


def _print_annotated(ann, inline: bool, comment_style: str) -> None:
    if inline:
        print(ann.inline_comment(style=comment_style))
        return

    status = green("✓") if ann.is_valid else red("✗")
    print(f"{status} {bold(ann.expression)}")
    print(f"   {dim('→')} {ann.description}")
    for w in ann.warnings:
        print(f"   {yellow('⚠')}  {w}")
    for s in ann.suggestions:
        print(f"   {dim('💡')} {s}")


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    expressions: list[str] = list(args.expression or [])

    if args.file:
        try:
            with open(args.file) as fh:
                for line in fh:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        expressions.append(line)
        except OSError as exc:
            print(f"Error reading file: {exc}", file=sys.stderr)
            sys.exit(1)

    if not expressions:
        parser.print_help()
        sys.exit(0)

    results = annotate_many(expressions)
    for ann in results:
        _print_annotated(ann, inline=args.inline, comment_style=args.comment_style)
    if not args.inline and len(results) > 1:
        valid_count = sum(1 for a in results if a.is_valid)
        print(dim(f"\n{valid_count}/{len(results)} expressions valid."))


if __name__ == "__main__":  # pragma: no cover
    main()
