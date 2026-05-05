"""Tests for crontab_viz.template."""

import pytest
from crontab_viz.template import (
    Template,
    list_templates,
    find_by_name,
    find_by_tag,
    categories,
    format_table,
)


def test_list_templates_returns_all():
    templates = list_templates()
    assert len(templates) > 0


def test_list_templates_filter_by_category():
    daily = list_templates(category="daily")
    assert all(t.category == "daily" for t in daily)
    assert len(daily) >= 1


def test_list_templates_unknown_category_empty():
    result = list_templates(category="nonexistent")
    assert result == []


def test_find_by_name_exists():
    t = find_by_name("hourly")
    assert t is not None
    assert t.name == "hourly"
    assert t.expression == "@hourly"


def test_find_by_name_missing_returns_none():
    assert find_by_name("does_not_exist") is None


def test_find_by_tag_returns_matching():
    results = find_by_tag("daily")
    assert len(results) >= 1
    assert all("daily" in t.tags for t in results)


def test_find_by_tag_unknown_returns_empty():
    assert find_by_tag("no_such_tag") == []


def test_categories_returns_sorted_unique():
    cats = categories()
    assert cats == sorted(set(cats))
    assert "daily" in cats
    assert "weekly" in cats
    assert "monthly" in cats


def test_format_table_contains_header():
    table = format_table()
    assert "NAME" in table
    assert "EXPRESSION" in table
    assert "DESCRIPTION" in table


def test_format_table_contains_template_names():
    table = format_table()
    assert "hourly" in table
    assert "daily_midnight" in table


def test_format_table_subset():
    subset = [find_by_name("hourly"), find_by_name("yearly")]
    table = format_table(subset)
    assert "hourly" in table
    assert "yearly" in table
    assert "every_minute" not in table


def test_format_table_empty_list():
    table = format_table([])
    assert "No templates found" in table


def test_template_dataclass_fields():
    t = find_by_name("weekdays_9am")
    assert t is not None
    assert isinstance(t.tags, list)
    assert "weekday" in t.tags
    assert t.category == "weekly"
