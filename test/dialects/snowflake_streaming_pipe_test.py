"""Snowpipe Streaming COPY sources."""

import pytest

from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.parser import rust_parser
from sqlfluff.core.parser.rust_parser import _HAS_RUST_PARSER


@pytest.mark.parametrize(
    "sql",
    [
        "CREATE PIPE p AS COPY INTO t FROM TABLE(DATA_SOURCE(TYPE => 'STREAMING')) "
        "MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;",
        "CREATE PIPE p AS COPY INTO t "
        "FROM (SELECT $1 FROM TABLE(DATA_SOURCE(TYPE => 'STREAMING')));",
        "CREATE PIPE p AS COPY INTO t FROM @stage FILE_FORMAT=(TYPE=JSON);",
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
def test_streaming_pipe_sources(sql, rust, monkeypatch):
    """Parse direct and transformed streaming sources and a staged control."""
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
    assert len(list(result.tree.recursive_crawl("copy_into_table_statement"))) == 1
    assert bool(calls) is rust, "Unexpected parser backend"
