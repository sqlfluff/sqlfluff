"""Regional S3 locations retain their bucket path type across statements."""

import pytest

from sqlfluff.core import FluffConfig, Linter

try:
    from sqlfluff.core.parser.rust_parser import _HAS_RUST_PARSER
except ImportError:  # pragma: no cover
    _HAS_RUST_PARSER = False


@pytest.mark.parametrize(
    "rust",
    [
        pytest.param(False, id="python"),
        pytest.param(
            True,
            id="rust",
            marks=pytest.mark.skipif(
                not _HAS_RUST_PARSER, reason="Rust parser not available"
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    "protocol,partition",
    [("s3", "aws"), ("s3china", "aws-cn"), ("s3gov", "aws-us-gov")],
    ids=["s3", "s3china", "s3gov"],
)
@pytest.mark.parametrize(
    "sql",
    [
        "CREATE STAGE example URL = '{url}';",
        "ALTER STAGE example SET URL = '{url}';",
        "CREATE STORAGE INTEGRATION example TYPE = EXTERNAL_STAGE "
        "STORAGE_PROVIDER = '{provider}' ENABLED = TRUE "
        "STORAGE_AWS_ROLE_ARN = 'arn:{partition}:iam::123456789012:role/example' "
        "STORAGE_ALLOWED_LOCATIONS = ('{url}') "
        "STORAGE_BLOCKED_LOCATIONS = ('{url}private/');",
        "ALTER STORAGE INTEGRATION example SET "
        "STORAGE_ALLOWED_LOCATIONS = ('{url}') "
        "STORAGE_BLOCKED_LOCATIONS = ('{url}private/');",
        "COPY INTO example FROM '{url}';",
        "COPY INTO '{url}' FROM example;",
    ],
    ids=[
        "create-stage",
        "alter-stage",
        "create-integration",
        "alter-integration",
        "copy-into-table",
        "copy-into-location",
    ],
)
def test_s3_bucket_paths(rust, protocol, partition, sql):
    """Locations parse as bucket paths in stage, integration, and COPY statements."""
    url = f"{protocol}://example-bucket/path/"
    sql = sql.format(url=url, provider=protocol.upper(), partition=partition)
    config = FluffConfig(overrides={"dialect": "snowflake", "use_rust_parser": rust})
    parsed = Linter(config=config).parse_string(sql)
    assert not parsed.violations
    assert not list(parsed.tree.recursive_crawl("unparsable"))
    paths = [segment.raw for segment in parsed.tree.recursive_crawl("bucket_path")]
    expected = [f"'{url}'"]
    if "STORAGE_BLOCKED_LOCATIONS" in sql:
        expected.append(f"'{url}private/'")
    assert paths == expected
