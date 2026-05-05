"""Tests for crontab_viz.tags."""

from __future__ import annotations

import pytest

from crontab_viz.parser import parse
from crontab_viz.tags import (
    TaggedExpression,
    all_tags,
    auto_tag,
    filter_by_tag,
    tag_expression,
)


def _parse(expr: str):
    return parse(expr)


def test_auto_tag_every_minute():
    tags = auto_tag(_parse("* * * * *"))
    assert "every-minute" in tags


def test_auto_tag_hourly():
    tags = auto_tag(_parse("0 * * * *"))
    assert "hourly" in tags
    assert "every-minute" not in tags


def test_auto_tag_daily():
    tags = auto_tag(_parse("0 9 * * *"))
    assert "daily" in tags


def test_auto_tag_weekly():
    tags = auto_tag(_parse("0 9 * * 1"))
    assert "weekly" in tags


def test_auto_tag_monthly():
    tags = auto_tag(_parse("0 0 1 * *"))
    assert "monthly" in tags


def test_tag_expression_includes_user_tags():
    parsed = _parse("0 9 * * *")
    te = tag_expression("0 9 * * *", parsed, user_tags=["backup", "prod"])
    assert "backup" in te.user_tags
    assert "prod" in te.user_tags


def test_tag_expression_user_tags_lowercased():
    parsed = _parse("0 9 * * *")
    te = tag_expression("0 9 * * *", parsed, user_tags=["BACKUP"])
    assert "backup" in te.user_tags


def test_all_tags_combines_auto_and_user():
    parsed = _parse("0 9 * * *")
    te = tag_expression("0 9 * * *", parsed, user_tags=["important"])
    combined = te.all_tags
    assert "important" in combined
    assert "daily" in combined


def test_has_tag_true():
    parsed = _parse("* * * * *")
    te = tag_expression("* * * * *", parsed)
    assert te.has_tag("every-minute")


def test_has_tag_false():
    parsed = _parse("* * * * *")
    te = tag_expression("* * * * *", parsed)
    assert not te.has_tag("monthly")


def test_filter_by_tag():
    items = [
        tag_expression("* * * * *", _parse("* * * * *")),
        tag_expression("0 9 * * *", _parse("0 9 * * *")),
        tag_expression("0 0 1 * *", _parse("0 0 1 * *")),
    ]
    daily = filter_by_tag(items, "daily")
    assert len(daily) == 1
    assert daily[0].expression == "0 9 * * *"


def test_filter_by_tag_empty_result():
    items = [tag_expression("* * * * *", _parse("* * * * *"))]
    result = filter_by_tag(items, "monthly")
    assert result == []


def test_all_tags_across_items():
    items = [
        tag_expression("* * * * *", _parse("* * * * *"), user_tags=["realtime"]),
        tag_expression("0 9 * * *", _parse("0 9 * * *"), user_tags=["morning"]),
    ]
    tags = all_tags(items)
    assert "realtime" in tags
    assert "morning" in tags
    assert "every-minute" in tags
    assert tags == sorted(set(tags))  # sorted and deduplicated
