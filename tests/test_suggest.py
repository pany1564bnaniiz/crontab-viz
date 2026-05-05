"""Tests for crontab_viz.suggest."""

import pytest

from crontab_viz.suggest import Suggestion, suggest, format_suggestions


# ---------------------------------------------------------------------------
# suggest()
# ---------------------------------------------------------------------------

def test_suggest_empty_query_returns_defaults():
    results = suggest("")
    assert len(results) > 0
    assert all(isinstance(s, Suggestion) for s in results)


def test_suggest_wildcard_query_returns_defaults():
    assert suggest("*") == suggest("")


def test_suggest_top_n_respected():
    results = suggest("", top_n=3)
    assert len(results) <= 3


def test_suggest_every_minute():
    results = suggest("every minute")
    assert results, "Expected at least one suggestion"
    assert results[0].expression == "* * * * *"


def test_suggest_hourly():
    results = suggest("every hour")
    assert any(s.expression == "0 * * * *" for s in results)


def test_suggest_daily():
    results = suggest("midnight")
    assert any("0 0" in s.expression for s in results)


def test_suggest_business_hours():
    results = suggest("business hours")
    assert any(s.expression == "0 9-17 * * 1-5" for s in results)


def test_suggest_no_match_returns_empty():
    results = suggest("xyzzy frobnicator")
    assert results == []


def test_suggest_exact_expression_match():
    results = suggest("*/5 * * * *")
    assert results
    assert results[0].expression == "*/5 * * * *"


def test_suggest_returns_suggestion_dataclass_fields():
    result = suggest("reboot")[0]
    assert hasattr(result, "expression")
    assert hasattr(result, "label")
    assert hasattr(result, "description")


# ---------------------------------------------------------------------------
# format_suggestions()
# ---------------------------------------------------------------------------

def test_format_suggestions_empty_list():
    output = format_suggestions([])
    assert "No suggestions" in output


def test_format_suggestions_contains_expression():
    suggestions = suggest("every minute")
    output = format_suggestions(suggestions, color=False)
    assert "* * * * *" in output


def test_format_suggestions_contains_label():
    suggestions = suggest("every hour")
    output = format_suggestions(suggestions, color=False)
    assert "every hour" in output


def test_format_suggestions_header_present():
    suggestions = suggest("")
    output = format_suggestions(suggestions, color=False)
    assert "Suggestions" in output
