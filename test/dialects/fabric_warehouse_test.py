"""Regression tests for constructs `fabric_warehouse` must reject.

The fixture-based auto-discovery in `dialects_test.py` only covers SQL that
is expected to parse *successfully* -- there's no fixture-file convention
for asserting a parse failure. These three cases were found by an
automated code review of the initial version of this dialect (each one
was, at the time, incorrectly accepted because a segment was inherited
unchanged from `tsql` rather than narrowed for Fabric Warehouse) and are
pinned here as permanent regressions, following the same pattern as
`test__dialect__rejects_trailing_comma_after_final_cte` above.
"""

import pytest

from sqlfluff.core import Linter


@pytest.mark.parametrize(
    "sql",
    [
        # Fabric Warehouse has no user-managed indexes at all -- an inline
        # INDEX clause on a column definition must not parse, even though
        # T-SQL's own ColumnDefinitionSegment permits it.
        "CREATE TABLE dbo.t (a INT NOT NULL INDEX idx_a NONCLUSTERED (a));",
        # FOREIGN KEY constraints in Fabric Warehouse are NOT ENFORCED
        # only -- there is no referential action to configure, so
        # ON DELETE / ON UPDATE / NOT FOR REPLICATION must not parse even
        # though T-SQL's ReferencesConstraintGrammar allows them.
        "ALTER TABLE dbo.t ADD CONSTRAINT FK_t FOREIGN KEY (a) "
        "REFERENCES dbo.t2 (a) ON DELETE CASCADE NOT ENFORCED;",
    ],
)
def test__dialect__fabric_warehouse_rejects_unsupported_constructs(sql: str) -> None:
    """Ensure constructs absent from Fabric Warehouse's documented syntax fail to parse."""
    parsed = Linter(dialect="fabric_warehouse").parse_string(sql)
    parsing_errors = [v for v in parsed.violations if v.rule_code() == "PRS"]
    assert parsing_errors


def test__dialect__fabric_warehouse_ctas_accepts_renamed_columns() -> None:
    """CTAS output-column renaming must not require a datatype per column.

    CTAS always derives column types from the SELECT, so the optional
    column list is name-only (for renaming), not a full column definition.
    """
    sql = (
        "CREATE TABLE dbo.t2 (renamed_a, renamed_b) AS "
        "SELECT a, b FROM dbo.t;"
    )
    parsed = Linter(dialect="fabric_warehouse").parse_string(sql)
    parsing_errors = [v for v in parsed.violations if v.rule_code() == "PRS"]
    assert not parsing_errors
