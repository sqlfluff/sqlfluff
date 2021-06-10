"""Tests specific to the postgres dialect."""

import pytest

from sqlfluff.core import FluffConfig, Linter


@pytest.mark.parametrize(
    "raw",
    [
        "SELECT t1.field, EXTRACT(EPOCH FROM t1.sometime) AS myepoch FROM t1",
        "SELECT t1.field, EXTRACT(EPOCH FROM t1.sometime - t1.othertime) AS myepoch FROM t1",
    ],
)
def test_epoch_datetime_unit(raw):
    """Test the EPOCH keyword for postgres dialect."""
    # Don't test for new lines or capitalisation
    cfg = FluffConfig(
        configs={"core": {"exclude_rules": "L009,L016,L036", "dialect": "postgres"}}
    )
    lnt = Linter(config=cfg)
    result = lnt.lint_string(raw)
    assert result.num_violations() == 0


@pytest.mark.parametrize(
    "raw",
    [
        "SELECT foo AS space FROM t1",
        "SELECT space.something FROM t1 AS space",
    ],
)
def test_space_is_not_reserved(raw):
    """Ensure that SPACE is not treated as reserved."""
    cfg = FluffConfig(
        configs={"core": {"exclude_rules": "L009,L016,L031", "dialect": "postgres"}}
    )
    lnt = Linter(config=cfg)
    result = lnt.lint_string(raw)
    assert result.num_violations() == 0


@pytest.mark.parametrize(
    "raw",
    [
        "CREATE TABLE t1 (goo text, pay_by_quarter integer[], schedule text[][])",
        "CREATE TABLE t1 (goo text, pay_by_quarter integer ARRAY, schedule text[3][3])",
        "CREATE TABLE t1 (goo text, pay_by_quarter integer ARRAY[4], schedule text[][])",
    ],
)
def test_array_type(raw):
    """Ensure that array types can be declared."""
    cfg = FluffConfig(
        configs={"core": {"exclude_rules": "L009,L016,L031", "dialect": "postgres"}}
    )
    lnt = Linter(config=cfg)
    result = lnt.lint_string(raw)
    assert result.num_violations() == 0


@pytest.mark.parametrize(
    "raw",
    [
        "SELECT '{1, 2, 3}'::integer[] FROM t1",
    ],
)
def test_array_cast(raw):
    """Ensure that ARRAY is not treated as reserved."""
    cfg = FluffConfig(
        configs={"core": {"exclude_rules": "L009,L016,L031", "dialect": "postgres"}}
    )
    lnt = Linter(config=cfg)
    result = lnt.lint_string(raw)
    assert result.num_violations() == 0


@pytest.mark.parametrize(
    "raw",
    [
        "SELECT ARRAY[1, 2, 3] AS int_array FROM t1",
        "SELECT ARRAY['a', 'b', 'c'] AS string_array FROM t1",
    ],
)
def test_array_literal(raw):
    """Ensure that ARRAY is not treated as reserved."""
    cfg = FluffConfig(
        configs={"core": {"exclude_rules": "L009,L016,L031", "dialect": "postgres"}}
    )
    lnt = Linter(config=cfg)
    result = lnt.lint_string(raw)
    assert result.num_violations() == 0
