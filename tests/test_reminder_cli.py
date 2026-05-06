"""Tests for crontab_viz.reminder_cli."""
import pytest

from crontab_viz.reminder_cli import build_parser, main
from crontab_viz.reminder import clear_reminders, load_reminders


@pytest.fixture(autouse=True)
def patch_default_path(tmp_path, monkeypatch):
    """Redirect all reminder I/O to a temp file."""
    p = str(tmp_path / "reminders.json")
    monkeypatch.setattr("crontab_viz.reminder.DEFAULT_PATH", p)
    monkeypatch.setattr("crontab_viz.reminder_cli.add_reminder",
                        __import__("functools").partial(
                            __import__("crontab_viz.reminder", fromlist=["add_reminder"]).add_reminder,
                        ))
    yield p


def test_build_parser_has_subcommands():
    parser = build_parser()
    assert parser is not None


def test_main_add_valid_expression(tmp_path, monkeypatch, capsys):
    path = str(tmp_path / "r.json")
    monkeypatch.setattr("crontab_viz.reminder.DEFAULT_PATH", path)
    monkeypatch.setattr("crontab_viz.reminder_cli.add_reminder",
                        lambda expr, note, tags=None: \
                        __import__("crontab_viz.reminder", fromlist=["add_reminder"]).add_reminder(
                            expr, note, tags=tags, path=path))
    with pytest.raises(SystemExit) as exc:
        main(["add", "0 * * * *", "Check hourly"])
    assert exc.value.code == 0


def test_main_add_invalid_expression_exits_nonzero(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["add", "99 99 99 99 99", "bad"])
    assert exc.value.code != 0


def test_main_list_empty(tmp_path, monkeypatch, capsys):
    path = str(tmp_path / "r.json")
    monkeypatch.setattr("crontab_viz.reminder_cli.load_reminders",
                        lambda expression=None: [])
    with pytest.raises(SystemExit):
        main(["list"])
    captured = capsys.readouterr()
    assert "No reminders" in captured.out


def test_main_remove_nonexistent_exits_nonzero(tmp_path, monkeypatch):
    monkeypatch.setattr("crontab_viz.reminder_cli.remove_reminder",
                        lambda expr, note: False)
    with pytest.raises(SystemExit) as exc:
        main(["remove", "* * * * *", "ghost"])
    assert exc.value.code != 0


def test_main_clear(tmp_path, monkeypatch, capsys):
    cleared = []
    monkeypatch.setattr("crontab_viz.reminder_cli.clear_reminders",
                        lambda: cleared.append(True))
    with pytest.raises(SystemExit):
        main(["clear"])
    assert cleared
