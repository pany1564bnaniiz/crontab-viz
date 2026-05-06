"""Tests for crontab_viz.reminder."""
import os
import pytest

from crontab_viz.reminder import (
    Reminder,
    add_reminder,
    load_reminders,
    remove_reminder,
    clear_reminders,
)


@pytest.fixture()
def rem_file(tmp_path):
    return str(tmp_path / "reminders.json")


def test_add_reminder_creates_file(rem_file):
    add_reminder("0 * * * *", "Check logs", path=rem_file)
    assert os.path.exists(rem_file)


def test_add_reminder_stores_expression(rem_file):
    add_reminder("0 * * * *", "Check logs", path=rem_file)
    reminders = load_reminders(path=rem_file)
    assert reminders[0].expression == "0 * * * *"


def test_add_reminder_stores_note(rem_file):
    add_reminder("0 * * * *", "Check logs", path=rem_file)
    reminders = load_reminders(path=rem_file)
    assert reminders[0].note == "Check logs"


def test_add_reminder_stores_tags(rem_file):
    add_reminder("0 0 * * *", "Daily backup", tags=["backup", "daily"], path=rem_file)
    reminders = load_reminders(path=rem_file)
    assert "backup" in reminders[0].tags


def test_add_multiple_reminders(rem_file):
    add_reminder("* * * * *", "Every minute", path=rem_file)
    add_reminder("0 0 * * *", "Daily", path=rem_file)
    reminders = load_reminders(path=rem_file)
    assert len(reminders) == 2


def test_load_reminders_filter_by_expression(rem_file):
    add_reminder("* * * * *", "Every minute", path=rem_file)
    add_reminder("0 0 * * *", "Daily", path=rem_file)
    reminders = load_reminders(expression="0 0 * * *", path=rem_file)
    assert len(reminders) == 1
    assert reminders[0].note == "Daily"


def test_load_reminders_empty_file(rem_file):
    reminders = load_reminders(path=rem_file)
    assert reminders == []


def test_remove_reminder_returns_true(rem_file):
    add_reminder("* * * * *", "note", path=rem_file)
    result = remove_reminder("* * * * *", "note", path=rem_file)
    assert result is True


def test_remove_reminder_actually_removes(rem_file):
    add_reminder("* * * * *", "note", path=rem_file)
    remove_reminder("* * * * *", "note", path=rem_file)
    assert load_reminders(path=rem_file) == []


def test_remove_nonexistent_returns_false(rem_file):
    result = remove_reminder("* * * * *", "ghost", path=rem_file)
    assert result is False


def test_clear_reminders(rem_file):
    add_reminder("* * * * *", "a", path=rem_file)
    add_reminder("0 0 * * *", "b", path=rem_file)
    clear_reminders(path=rem_file)
    assert load_reminders(path=rem_file) == []


def test_reminder_to_dict_roundtrip():
    r = Reminder(expression="0 9 * * 1", note="standup", tags=["work"])
    d = r.to_dict()
    r2 = Reminder.from_dict(d)
    assert r2.expression == r.expression
    assert r2.note == r.note
    assert r2.tags == r.tags
