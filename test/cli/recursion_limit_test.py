import builtins
from types import SimpleNamespace

import pytest

from sqlfluff.cli.commands import apply_recursion_limit as apply_rl


class DummyConfig:
    def __init__(self, value):
        self._value = value

    def get(self, key, section=None, default=None):
        if key == "recursion_limit":
            return self._value
        return default


@pytest.fixture()
def echo_capture(monkeypatch):
    calls = []

    def fake_echo(msg, err=False):
        calls.append((msg, err))

    monkeypatch.setattr("sqlfluff.cli.commands.click.echo", fake_echo)
    return calls


def test_recursion_limit_from_cli_valid(monkeypatch):
    called = SimpleNamespace(value=None)

    def fake_set(limit):
        called.value = limit

    monkeypatch.setattr("sqlfluff.cli.commands.sys.setrecursionlimit", fake_set)
    # Should use CLI value directly
    apply_rl(2000, extra_config_path=None, ignore_local_config=False, kwargs={})
    assert called.value == 2000


def test_recursion_limit_from_config_valid(monkeypatch):
    called = SimpleNamespace(value=None)

    def fake_set(limit):
        called.value = limit

    monkeypatch.setattr("sqlfluff.cli.commands.sys.setrecursionlimit", fake_set)
    # Provide None to force reading from config; config returns string
    monkeypatch.setattr(
        "sqlfluff.cli.commands.get_config", lambda *a, **k: DummyConfig("2500")
    )
    apply_rl(None, extra_config_path=None, ignore_local_config=False, kwargs={})
    assert called.value == 2500


def test_recursion_limit_config_non_integer(monkeypatch, echo_capture):
    called = SimpleNamespace(called=False)

    def fake_set(limit):
        called.called = True

    monkeypatch.setattr("sqlfluff.cli.commands.sys.setrecursionlimit", fake_set)
    # Non-integer config should be ignored, and no echo emitted
    monkeypatch.setattr(
        "sqlfluff.cli.commands.get_config", lambda *a, **k: DummyConfig("abc")
    )
    apply_rl(None, extra_config_path=None, ignore_local_config=False, kwargs={})
    assert not called.called
    # No error output expected
    assert echo_capture == []


def test_recursion_limit_out_of_bounds(monkeypatch, echo_capture):
    called = SimpleNamespace(called=False)

    def fake_set(limit):
        called.called = True

    monkeypatch.setattr("sqlfluff.cli.commands.sys.setrecursionlimit", fake_set)
    # Above default max_limit=1_000_000 to trigger validation error
    apply_rl(1_000_001, extra_config_path=None, ignore_local_config=False, kwargs={})
    assert not called.called
    assert echo_capture and "Invalid recursion_limit" in echo_capture[0][0]
    assert echo_capture[0][1] is True


def test_recursion_limit_set_raises(monkeypatch, echo_capture):
    def fake_set(limit):
        raise RuntimeError("boom")

    monkeypatch.setattr("sqlfluff.cli.commands.sys.setrecursionlimit", fake_set)
    apply_rl(1500, extra_config_path=None, ignore_local_config=False, kwargs={})
    assert echo_capture and "Failed to set recursion_limit: boom" in echo_capture[0][0]
    assert echo_capture[0][1] is True
