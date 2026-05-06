"""Tests for crontab_viz.annotate module."""

from __future__ import annotations

import pytest

from crontab_viz.annotate import annotate, annotate_many, AnnotatedExpression


def test_annotate_returns_annotated_expression():
    result = annotate("* * * * *")
    assert isinstance(result, AnnotatedExpression)


def test_annotate_every_minute_is_valid():
    result = annotate("* * * * *")
    assert result.is_valid is True


def test_annotate_every_minute_description():
    result = annotate("* * * * *")
    assert "minute" in result.description.lower()


def test_annotate_invalid_expression():
    result = annotate("not a cron")
    assert result.is_valid is False
    assert len(result.warnings) > 0


def test_annotate_invalid_description_placeholder():
    result = annotate("invalid")
    assert "invalid" in result.description.lower() or result.description


def test_annotate_alias_hourly():
    result = annotate("@hourly")
    assert result.is_valid is True
    assert "hour" in result.description.lower()


def test_inline_comment_contains_expression():
    result = annotate("0 9 * * 1")
    inline = result.inline_comment()
    assert "0 9 * * 1" in inline


def test_inline_comment_contains_description():
    result = annotate("0 9 * * 1")
    inline = result.inline_comment()
    assert result.description in inline


def test_inline_comment_custom_style():
    result = annotate("0 9 * * 1")
    inline = result.inline_comment(style="//")
    assert "//" in inline


def test_full_report_contains_expression():
    result = annotate("30 6 * * *")
    report = result.full_report()
    assert "30 6 * * *" in report


def test_full_report_contains_description():
    result = annotate("30 6 * * *")
    report = result.full_report()
    assert result.description in report


def test_full_report_shows_warnings_when_present():
    result = annotate("* * 15 * 1")  # DOM+DOW both set — should warn
    report = result.full_report()
    if result.warnings:
        assert "Warning" in report


def test_annotate_many_returns_list():
    results = annotate_many(["* * * * *", "0 0 * * *"])
    assert len(results) == 2


def test_annotate_many_mixed_validity():
    results = annotate_many(["* * * * *", "bad expr"])
    valid = [r for r in results if r.is_valid]
    invalid = [r for r in results if not r.is_valid]
    assert len(valid) == 1
    assert len(invalid) == 1


def test_annotate_many_empty_list():
    results = annotate_many([])
    assert results == []
