"""CLI sub-tool for managing and listing cron aliases."""

from __future__ import annotations

import argparse
import sys

from crontab_viz import alias as alias_mod
from crontab_viz.colors import bold, dim, green, yellow


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="crontab-alias",
        description="List and manage cron expression aliases.",
    )
    sub = p.add_subparsers(dest="command")

    # list
    ls = sub.add_parser("list", help="List all known aliases")
    ls.add_argument(
        "--special",
        action="store_true",
        help="Include special aliases like @reboot that have no time expression",
    )

    # resolve
    res = sub.add_parser("resolve", help="Show the expression for an alias")
    res.add_argument("name", help="Alias name, e.g. @daily")

    # register
    reg = sub.add_parser("register", help="Register a custom alias (runtime only)")
    reg.add_argument("name", help="Alias name starting with '@'")
    reg.add_argument("expression", help="Cron expression, e.g. '30 6 * * 1-5'")

    return p


def _cmd_list(args: argparse.Namespace) -> None:
    entries = alias_mod.list_aliases(include_special=args.special)
    if not entries:
        print(dim("No aliases found."))
        return
    col_w = max(len(e.name) for e in entries) + 2
    print(bold(f"{'Alias':<{col_w}}  {'Expression':<20}  Source"))
    print(dim("-" * 55))
    for e in entries:
        expr_str = e.expression if e.expression else dim("(special)")
        source = dim("built-in") if e.builtin else yellow("custom")
        print(f"{green(e.name):<{col_w}}  {expr_str:<20}  {source}")


def _cmd_resolve(args: argparse.Namespace) -> None:
    expr = alias_mod.resolve(args.name)
    if expr is None:
        if alias_mod.is_alias(args.name):
            print(dim(f"{args.name} is a special alias with no time expression."))
        else:
            print(f"Unknown alias: {args.name}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"{bold(args.name)}  →  {expr}")


def _cmd_register(args: argparse.Namespace) -> None:
    try:
        alias_mod.register(args.name, args.expression)
        print(green(f"Registered {args.name} = {args.expression}"))
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "list":
        _cmd_list(args)
    elif args.command == "resolve":
        _cmd_resolve(args)
    elif args.command == "register":
        _cmd_register(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
