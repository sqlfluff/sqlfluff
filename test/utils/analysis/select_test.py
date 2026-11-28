"""Tests for the select statement analysis."""

import gc

from sqlfluff.core import FluffConfig, Linter
from sqlfluff.utils.analysis import select
from sqlfluff.utils.analysis.select import get_select_statement_info


def _select(sql: str):
    cfg = FluffConfig(overrides={"dialect": "ansi"})
    tree = Linter(config=cfg).parse_string(sql).tree
    return tree, next(tree.recursive_crawl("select_statement")), cfg.get("dialect_obj")


def test_select_info_cached_per_segment(monkeypatch):
    """A second call reuses the analysis but hands back fresh lists."""
    tree, seg, dialect = _select("SELECT a.x FROM t AS a")
    calls = []
    analyze = select._get_select_statement_info
    monkeypatch.setattr(
        select,
        "_get_select_statement_info",
        lambda *args: calls.append(args) or analyze(*args),
    )
    first = get_select_statement_info(seg, dialect)
    second = get_select_statement_info(seg, dialect)
    assert len(calls) == 1
    assert first == second
    assert first.select_statement is seg
    assert first.reference_buffer is not second.reference_buffer
    first.reference_buffer.clear()
    assert get_select_statement_info(seg, dialect).reference_buffer


def test_select_info_early_exit():
    """With no table aliases, early exit gives None but a full call doesn't."""
    tree, seg, dialect = _select("SELECT 1")
    assert get_select_statement_info(seg, dialect) is None
    info = get_select_statement_info(seg, dialect, early_exit=False)
    assert info is not None and info.select_targets
    assert get_select_statement_info(seg, dialect) is None


def test_select_info_evicted_with_segment():
    """An entry goes when its segment does."""
    tree, seg, dialect = _select("SELECT a.x FROM t AS a")
    get_select_statement_info(seg, dialect)
    key = (id(seg), dialect.name)
    assert key in select._INFO_CACHE
    del tree, seg
    gc.collect()
    assert key not in select._INFO_CACHE
