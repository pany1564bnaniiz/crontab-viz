"""Tests for crontab_viz.search."""

import pytest

from crontab_viz.search import search, format_results, SearchResult


EXPRESSIONS = [
    "* * * * *",
    "0 * * * *",
    "0 9 * * 1",
    "0 0 * * 0",
    "*/15 * * * *",
    "0 0 1 * *",
    "0 0 1 1 *",
]


def test_search_no_query_returns_all():
    results = search(EXPRESSIONS, query="")
    assert len(results) == len(EXPRESSIONS)


def test_search_every_minute_query():
    results = search(EXPRESSIONS, query="every minute")
    assert results, "Expected at least one result"
    assert results[0].expression == "* * * * *"


def test_search_hourly_query():
    results = search(EXPRESSIONS, query="hourly")
    assert any(r.expression == "0 * * * *" for r in results)


def test_search_weekly_tag_filter():
    results = search(EXPRESSIONS, tag_filter="weekly")
    for r in results:
        assert "weekly" in [t.lower() for t in r.tags]


def test_search_monthly_tag_filter():
    results = search(EXPRESSIONS, tag_filter="monthly")
    for r in results:
        assert "monthly" in [t.lower() for t in r.tags]


def test_search_invalid_expression_skipped():
    exprs = ["* * * * *", "not_a_cron", "0 * * * *"]
    results = search(exprs)
    expressions_found = [r.expression for r in results]
    assert "not_a_cron" not in expressions_found
    assert "* * * * *" in expressions_found


def test_search_score_ordering():
    results = search(EXPRESSIONS, query="minute")
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)


def test_search_tag_and_query_combined():
    results = search(EXPRESSIONS, query="midnight", tag_filter="daily")
    for r in results:
        assert "daily" in [t.lower() for t in r.tags]


def test_search_result_fields():
    results = search(["0 9 * * 1"])
    assert len(results) == 1
    r = results[0]
    assert r.expression == "0 9 * * 1"
    assert isinstance(r.description, str) and r.description
    assert isinstance(r.tags, list)
    assert isinstance(r.score, float)


def test_format_results_empty():
    output = format_results([])
    assert "No matching" in output


def test_format_results_contains_expression():
    results = search(["* * * * *"])
    output = format_results(results)
    assert "* * * * *" in output


def test_format_results_contains_tags():
    results = search(["* * * * *"])
    output = format_results(results)
    assert "tags:" in output
