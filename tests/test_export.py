"""Tests for crontab_viz.export."""

import json
import csv
import io
from datetime import datetime

import pytest
from crontab_viz.parser import parse
from crontab_viz.export import to_json, to_csv, export


BASE = datetime(2024, 1, 15, 12, 0, 0)
RAW = "*/5 * * * *"


def test_to_json_structure():
    expr = parse(RAW)
    result = to_json(expr, RAW, count=5, base=BASE)
    data = json.loads(result)
    assert data["expression"] == RAW
    assert "description" in data
    assert "base" in data
    assert len(data["occurrences"]) == 5


def test_to_json_occurrence_count():
    expr = parse(RAW)
    result = to_json(expr, RAW, count=3, base=BASE)
    data = json.loads(result)
    assert len(data["occurrences"]) == 3


def test_to_csv_structure():
    expr = parse(RAW)
    result = to_csv(expr, RAW, count=4, base=BASE)
    reader = csv.DictReader(io.StringIO(result))
    rows = list(reader)
    assert len(rows) == 4
    assert "expression" in rows[0]
    assert "description" in rows[0]
    assert "occurrence" in rows[0]


def test_to_csv_expression_column():
    expr = parse(RAW)
    result = to_csv(expr, RAW, count=2, base=BASE)
    reader = csv.DictReader(io.StringIO(result))
    for row in reader:
        assert row["expression"] == RAW


def test_export_json_dispatch():
    expr = parse(RAW)
    result = export(expr, RAW, fmt="json", count=2, base=BASE)
    data = json.loads(result)
    assert "occurrences" in data


def test_export_csv_dispatch():
    expr = parse(RAW)
    result = export(expr, RAW, fmt="csv", count=2, base=BASE)
    assert "expression" in result


def test_export_invalid_format():
    expr = parse(RAW)
    with pytest.raises(ValueError, match="Unsupported export format"):
        export(expr, RAW, fmt="xml", base=BASE)
