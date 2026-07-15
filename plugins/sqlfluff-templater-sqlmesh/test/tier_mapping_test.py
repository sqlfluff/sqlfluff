"""Tests for the T0-T3 source-mapping tiers of the SQLMesh templater.

Tier 0 splits the ``MODEL (...)`` header; tier 1 lints a macro-free body
verbatim; tier 2 substitutes inline-resolvable macros into the verbatim
source; tier 3 renders whole and maps the body as one coarse templated region.
"""

from pathlib import Path

import pytest
from sqlfluff_templater_sqlmesh.templater import SQLMeshTemplater

from sqlfluff.core import FluffConfig, Linter

# ---------------------------------------------------------------------------
# Unit tests for the header/macro scanners (no SQLMesh required).
# ---------------------------------------------------------------------------


def test_find_model_block_end_basic():
    """The MODEL(...) block boundary includes the trailing semicolon."""
    src = "MODEL (\n  name m,\n  kind VIEW\n);\n\nSELECT 1\n"
    end = SQLMeshTemplater._find_model_block_end(src)
    assert src[:end].strip().endswith(";")
    assert src[end:] == "SELECT 1\n"


def test_find_model_block_end_with_leading_comment():
    """A comment before MODEL must not defeat header detection."""
    src = "-- a leading comment\n/* block */\nMODEL (name m, kind VIEW);\nSELECT 1\n"
    end = SQLMeshTemplater._find_model_block_end(src)
    assert end is not None
    assert src[end:] == "SELECT 1\n"


def test_find_model_block_end_handles_nested_parens_and_strings():
    """Nested parens and semicolons inside strings don't end the block early."""
    src = (
        "MODEL (\n  name m,\n  kind INCREMENTAL_BY_TIME_RANGE (time_column c),\n"
        "  cron '@daily; not-the-end'\n);\nSELECT 1\n"
    )
    end = SQLMeshTemplater._find_model_block_end(src)
    assert src[end:] == "SELECT 1\n"


def test_find_model_block_end_returns_none_without_model():
    """Plain SQL (no MODEL header) yields no boundary."""
    assert SQLMeshTemplater._find_model_block_end("SELECT 1\n") is None


def test_find_macro_spans_detects_forms():
    """@name, @name(...), and @{...} are all detected."""
    body = "SELECT @{col}, @upper(name), x FROM t WHERE d >= @start_ds"
    spans = SQLMeshTemplater._find_macro_spans(body)
    found = [body[s:e] for s, e in spans]
    assert found == ["@{col}", "@upper(name)", "@start_ds"]


def test_find_macro_spans_ignores_strings_and_comments():
    """An @ inside a string or comment is not a macro."""
    body = "SELECT '@not_a_macro', x -- @also_not\nFROM t /* @nope */"
    assert SQLMeshTemplater._find_macro_spans(body) == []


# ---------------------------------------------------------------------------
# TemplatedFile assembly invariants (no SQLMesh required).
# ---------------------------------------------------------------------------


def _assert_coverage(tf):
    """Source and templated coverage must be contiguous and complete."""
    assert tf.sliced_file[0].source_slice.start == 0
    assert tf.sliced_file[0].templated_slice.start == 0
    assert tf.sliced_file[-1].source_slice.stop == len(tf.source_str)
    assert tf.sliced_file[-1].templated_slice.stop == len(tf.templated_str)
    for a, b in zip(tf.sliced_file, tf.sliced_file[1:]):
        assert a.source_slice.stop == b.source_slice.start
        assert a.templated_slice.stop == b.templated_slice.start


def test_passthrough_strips_header_keeps_body_literal():
    """Tier 0/1: header → zero-length templated, body → verbatim literal."""
    t = SQLMeshTemplater()
    src = "MODEL (name m, kind VIEW);\nSELECT 1 AS a\n"
    header_end = t._find_model_block_end(src)
    tf, errs = t._passthrough_file("m.sql", src, header_end)
    assert errs == []
    assert tf.templated_str == "SELECT 1 AS a\n"
    assert [s.slice_type for s in tf.sliced_file] == ["templated", "literal"]
    assert tf.sliced_file[0].templated_slice == slice(0, 0)
    _assert_coverage(tf)


def test_substitute_file_maps_each_span():
    """Tier 2: literal runs stay literal, each macro span becomes templated."""
    t = SQLMeshTemplater()
    src = "MODEL (name m);\nSELECT a FROM t WHERE d >= @start_ds\n"
    header_end = t._find_model_block_end(src)
    body = src[header_end:]
    spans = t._find_macro_spans(body)
    tf, errs = t._substitute_file("m.sql", src, header_end, spans, ["'2023-01-01'"])
    assert errs == []
    assert tf.templated_str == "SELECT a FROM t WHERE d >= '2023-01-01'\n"
    # exactly one templated span in the body, mapped to the substituted literal
    body_templated = [
        s
        for s in tf.sliced_file
        if s.slice_type == "templated" and s.source_slice.start >= header_end
    ]
    assert len(body_templated) == 1
    _assert_coverage(tf)


def test_coarse_templated_file_never_collapses():
    """Tier 3: whole body → one templated region covering the rendered SQL."""
    t = SQLMeshTemplater()
    src = "MODEL (name m);\nSELECT @EACH(['a'], x -> x)\n"
    header_end = t._find_model_block_end(src)
    tf, errs = t._coarse_templated_file("m.sql", src, header_end, "SELECT 'a'")
    assert errs == []
    assert tf.templated_str == "SELECT 'a'"
    assert all(s.slice_type == "templated" for s in tf.sliced_file)
    _assert_coverage(tf)


# ---------------------------------------------------------------------------
# End-to-end tier behaviour against real SQLMesh fixtures.
# ---------------------------------------------------------------------------


@pytest.fixture
def fixture_dir():
    """Path to the SQLMesh fixture project."""
    return Path(__file__).parent / "fixtures" / "sqlmesh"


@pytest.fixture
def sqlmesh_config(fixture_dir):
    """FluffConfig wired to the fixture project."""
    return {
        "core": {"templater": "sqlmesh", "dialect": "duckdb"},
        "templater": {
            "sqlmesh": {
                "project_dir": str(fixture_dir),
                "config": "config",
                "gateway": "local",
            }
        },
    }


def _process(fixture_dir, sqlmesh_config, model):
    templater = SQLMeshTemplater()
    config = FluffConfig(configs=sqlmesh_config)
    templater.sqlfluff_config = config
    templater.project_dir = str(fixture_dir)
    path = fixture_dir / "models" / model
    return templater.process(fname=str(path), in_str=path.read_text(), config=config)


def test_tier1_plain_model_is_verbatim(fixture_dir, sqlmesh_config):
    """A macro-free model is passed through unchanged (tier 1)."""
    pytest.importorskip("sqlmesh")
    tf, errs = _process(fixture_dir, sqlmesh_config, "simple_model.sql")
    assert errs == []
    body_start = SQLMeshTemplater._find_model_block_end(tf.source_str)
    # The templated string is exactly the source body, untouched.
    assert tf.templated_str == tf.source_str[body_start:]
    assert [s.slice_type for s in tf.sliced_file] == ["templated", "literal"]
    _assert_coverage(tf)


def test_tier2_scalar_macros_keep_literal_positions(fixture_dir, sqlmesh_config):
    """A model whose macros all resolve inline keeps its literal SQL literal."""
    pytest.importorskip("sqlmesh")
    tf, errs = _process(fixture_dir, sqlmesh_config, "incremental_model.sql")
    assert errs == []
    types = {s.slice_type for s in tf.sliced_file}
    # Both real literal SQL and substituted macro spans are present.
    assert "literal" in types and "templated" in types
    # Macros are gone from the templated output; it is parseable SQL.
    assert "@" not in tf.templated_str
    _assert_coverage(tf)


def test_tier3_structural_macro_is_coarse(fixture_dir, sqlmesh_config):
    """A model with a structural macro (@EACH) falls back to coarse mapping."""
    pytest.importorskip("sqlmesh")
    tf, errs = _process(fixture_dir, sqlmesh_config, "model_with_macros.sql")
    assert errs == []
    # Header + a single coarse templated body region; nothing linted literally.
    assert all(s.slice_type == "templated" for s in tf.sliced_file)
    assert "@" not in tf.templated_str
    _assert_coverage(tf)


def test_tier1_positions_are_accurate_end_to_end(fixture_dir, sqlmesh_config):
    """A tier-1 violation reports its real source position, not L1:P1.

    ``self_alias.sql`` has ``id AS id`` on line 7 of the source, which AL09
    flags. The whole point of tier 1 is that this maps back to line 7 rather
    than collapsing to the start of the file (the pre-tier behaviour).
    """
    pytest.importorskip("sqlmesh")
    linter = Linter(config=FluffConfig(configs=sqlmesh_config))
    path = fixture_dir / "models" / "self_alias.sql"
    linted = linter.lint_path(str(path)).files[0]
    al09 = [v for v in linted.get_violations() if v.rule_code() == "AL09"]
    assert al09, [v.rule_code() for v in linted.get_violations()]
    assert al09[0].line_no == 7
