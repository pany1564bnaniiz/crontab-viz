"""CLI helpers for the search sub-command."""

from __future__ import annotations

import argparse
from typing import List, Optional

from crontab_viz.search import search, format_results
from crontab_viz.tag_store import load_tagged
from crontab_viz.colors import bold, cyan, yellow


def build_search_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the *search* sub-command on *subparsers*."""
    p = subparsers.add_parser(
        "search",
        help="Search saved cron expressions by keyword or tag",
    )
    p.add_argument(
        "query",
        nargs="?",
        default="",
        help="Free-text query (description or expression keywords)",
    )
    p.add_argument(
        "--tag",
        dest="tag_filter",
        default=None,
        metavar="TAG",
        help="Filter results to expressions carrying this tag",
    )
    p.add_argument(
        "--file",
        dest="store_file",
        default=None,
        metavar="PATH",
        help="Path to the tag-store JSON file (default: ~/.crontab_viz_tags.json)",
    )
    p.set_defaults(func=_run_search)


def _run_search(args: argparse.Namespace) -> int:
    """Execute the search sub-command.  Returns an exit code."""
    kwargs = {}
    if args.store_file:
        kwargs["store_file"] = args.store_file

    tagged_list = load_tagged(**kwargs)  # type: ignore[arg-type]
    expressions: List[str] = [te.expression for te in tagged_list]

    if not expressions:
        print(yellow("No saved expressions found. Use 'tag' sub-command to save some."))
        return 0

    results = search(
        expressions,
        query=args.query,
        tag_filter=args.tag_filter,
    )

    if not results:
        print(yellow(f"No results for query={args.query!r} tag={args.tag_filter!r}."))
        return 0

    header = bold(cyan(f"Found {len(results)} result(s):"))
    print(header)
    print(format_results(results))
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    """Standalone entry-point for quick testing."""
    parser = argparse.ArgumentParser(prog="crontab-search")
    sub = parser.add_subparsers()
    build_search_parser(sub)
    args = parser.parse_args(argv)
    if hasattr(args, "func"):
        return args.func(args)
    parser.print_help()
    return 0
