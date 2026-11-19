"""Snowflake interactive table statements."""

import pytest

from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.parser import rust_parser
from sqlfluff.core.parser.rust_parser import _HAS_RUST_PARSER


@pytest.mark.parametrize(
    "sql",
    [
        "CREATE INTERACTIVE TABLE t (id INT) CLUSTER BY (id) AS SELECT 1 AS id;",
        "CREATE INTERACTIVE TABLE t (id INT) CLUSTER BY (id);",
        "CREATE INTERACTIVE TABLE t (id INT) CLUSTER BY (id) ROW_TIMESTAMP = TRUE;",
        "CREATE INTERACTIVE TABLE t CLUSTER BY (id) TARGET_LAG = '5 minutes' "
        "WAREHOUSE = wh AS SELECT id FROM source;",
        "CREATE TABLE t (id INT) CLUSTER BY (id) AS SELECT 1 AS id;",
    ],
)
@pytest.mark.parametrize(
    "rust",
    [
        False,
        pytest.param(
            True,
            marks=pytest.mark.skipif(
                not _HAS_RUST_PARSER, reason="Rust parser unavailable"
            ),
        ),
    ],
)
def test_interactive_tables(sql, rust, monkeypatch):
    """Parse interactive variants and an ordinary table control."""
    calls = []
    if _HAS_RUST_PARSER:
        original_parse = rust_parser.RustParser.parse

        def record_parse(*args, **kwargs):
            calls.append(True)
            return original_parse(*args, **kwargs)

        monkeypatch.setattr(rust_parser.RustParser, "parse", record_parse)

    config = FluffConfig(overrides={"dialect": "snowflake", "use_rust_parser": rust})
    result = Linter(config=config).parse_string(sql)
    assert result.tree is not None
    assert not result.violations
    assert result.tree.raw == sql
    assert len(list(result.tree.recursive_crawl("create_table_statement"))) == 1
    assert bool(calls) is rust, "Unexpected parser backend"
