"""Tests for crontab_viz.alias and crontab_viz.alias_cli."""

from __future__ import annotations

import pytest

import crontab_viz.alias as alias_mod
from crontab_viz.alias_cli import build_parser, main


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _cleanup(name: str):
    """Remove a custom alias if present (test isolation)."""
    alias_mod.unregister(name)


# ---------------------------------------------------------------------------
# alias.resolve
# ---------------------------------------------------------------------------

def test_resolve_builtin_daily():
    assert alias_mod.resolve("@daily") == "0 0 * * *"


def test_resolve_builtin_hourly():
    assert alias_mod.resolve("@hourly") == "0 * * * *"


def test_resolve_case_insensitive():
    assert alias_mod.resolve("@DAILY") == "0 0 * * *"


def test_resolve_unknown_returns_none():
    assert alias_mod.resolve("@nonexistent") is None


def test_resolve_special_reboot_returns_none():
    assert alias_mod.resolve("@reboot") is None


# ---------------------------------------------------------------------------
# alias.register / unregister
# ---------------------------------------------------------------------------

def test_register_custom_alias():
    alias_mod.register("@workday", "0 9 * * 1-5")
    assert alias_mod.resolve("@workday") == "0 9 * * 1-5"
    _cleanup("@workday")


def test_register_overrides_builtin_raises():
    with pytest.raises(ValueError, match="built-in"):
        alias_mod.register("@daily", "0 0 * * *")


def test_register_without_at_raises():
    with pytest.raises(ValueError, match="@"):
        alias_mod.register("nodaily", "0 0 * * *")


def test_unregister_returns_true_when_existed():
    alias_mod.register("@tmp", "* * * * *")
    assert alias_mod.unregister("@tmp") is True


def test_unregister_returns_false_when_missing():
    assert alias_mod.unregister("@ghost") is False


# ---------------------------------------------------------------------------
# alias.list_aliases
# ---------------------------------------------------------------------------

def test_list_aliases_contains_builtins():
    names = [e.name for e in alias_mod.list_aliases()]
    assert "@daily" in names
    assert "@hourly" in names


def test_list_aliases_excludes_special_by_default():
    names = [e.name for e in alias_mod.list_aliases()]
    assert "@reboot" not in names


def test_list_aliases_includes_special_when_requested():
    names = [e.name for e in alias_mod.list_aliases(include_special=True)]
    assert "@reboot" in names


def test_list_aliases_sorted():
    entries = alias_mod.list_aliases()
    names = [e.name for e in entries]
    assert names == sorted(names)


# ---------------------------------------------------------------------------
# alias.is_alias
# ---------------------------------------------------------------------------

def test_is_alias_known():
    assert alias_mod.is_alias("@weekly") is True


def test_is_alias_unknown():
    assert alias_mod.is_alias("@foobar") is False


# ---------------------------------------------------------------------------
# alias_cli
# ---------------------------------------------------------------------------

def test_build_parser_returns_parser():
    p = build_parser()
    assert p is not None


def test_main_list_runs(capsys):
    main(["list"])
    out = capsys.readouterr().out
    assert "@daily" in out


def test_main_resolve_known(capsys):
    main(["resolve", "@hourly"])
    out = capsys.readouterr().out
    assert "0 * * * *" in out


def test_main_resolve_unknown_exits():
    with pytest.raises(SystemExit):
        main(["resolve", "@doesnotexist"])


def test_main_register_and_list(capsys):
    main(["register", "@lunchtime", "0 12 * * 1-5"])
    main(["list"])
    out = capsys.readouterr().out
    assert "@lunchtime" in out
    _cleanup("@lunchtime")
