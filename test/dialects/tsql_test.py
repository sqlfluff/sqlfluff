"""Tests specific to the postgres dialect."""

import pytest

from sqlfluff.core import FluffConfig, Linter



def test_space_is_not_reserved(raw):
    """Ensure that SPACE is not treated as reserved."""
    cfg = FluffConfig(
        configs={"core": {"exclude_rules": "L009,L016,L031", "dialect": "tsql"}}
    )
    lnt = Linter(config=cfg)
    result = lnt.lint_string(raw)
    assert result.num_violations() == 0
