"""Tests for crontab_viz.lint."""

import pytest

from crontab_viz.lint import LintResult, lint


# ---------------------------------------------------------------------------
# LintResult helpers
# ---------------------------------------------------------------------------

def test_lint_result_bool_clean():
    r = LintResult(expression="0 * * * *")
    assert bool(r) is True


def test_lint_result_bool_with_warning():
    r = LintResult(expression="0 * * * *", warnings=["something"])
    assert bool(r) is False


def test_summary_ok():
    r = LintResult(expression="0 * * * *")
    assert r.summary().startswith("OK")


def test_summary_with_warning():
    r = LintResult(expression="* * * * *", warnings=["runs every minute"])
    summary = r.summary()
    assert "WARN" in summary
    assert "[warning]" in summary


def test_summary_with_suggestion():
    r = LintResult(expression="0 0 * * *", suggestions=["use @daily"])
    summary = r.summary()
    assert "[suggestion]" in summary


# ---------------------------------------------------------------------------
# High-frequency check
# ---------------------------------------------------------------------------

def test_every_minute_triggers_warning():
    result = lint("* * * * *")
    assert not result
    assert any("every minute" in w.lower() for w in result.warnings)


def test_hourly_no_frequency_warning():
    result = lint("0 * * * *")
    # no high-frequency warning
    assert not any("every minute" in w.lower() for w in result.warnings)


# ---------------------------------------------------------------------------
# DOM+DOW conflict check
# ---------------------------------------------------------------------------

def test_dom_dow_conflict_warning():
    result = lint("0 9 15 * 1")  # 15th of month AND Mondays
    assert any("day-of-month" in w.lower() or "dow" in w.lower() or "OR" in w
               for w in result.warnings)


def test_no_dom_dow_conflict_when_only_dom():
    result = lint("0 9 15 * *")
    assert not any("OR semantics" in w for w in result.warnings)


def test_no_dom_dow_conflict_when_only_dow():
    result = lint("0 9 * * 1")
    assert not any("OR semantics" in w for w in result.warnings)


# ---------------------------------------------------------------------------
# Midnight / @daily suggestion
# ---------------------------------------------------------------------------

def test_midnight_suggests_daily_alias():
    result = lint("0 0 * * *")
    assert any("@daily" in s for s in result.suggestions)


def test_non_midnight_no_daily_suggestion():
    result = lint("0 1 * * *")
    assert not any("@daily" in s for s in result.suggestions)


# ---------------------------------------------------------------------------
# Parse error handling
# ---------------------------------------------------------------------------

def test_invalid_expression_returns_warning():
    result = lint("not a cron")
    assert not result
    assert any("parse error" in w.lower() for w in result.warnings)


def test_too_few_fields_returns_warning():
    result = lint("* * *")
    assert not result
