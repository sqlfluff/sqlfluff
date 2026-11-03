"""Hive dialect tests outside the SQL/YAML parse fixtures.

Positive/valid-SQL cases belong in test/fixtures/dialects/hive/.
"""

import pytest

from sqlfluff.core import Linter


def _parses_cleanly(sql: str) -> bool:
    parsed = Linter(dialect="hive").parse_string(sql)
    violations = [v for v in parsed.violations if v.rule_code() == "PRS"]
    if parsed.tree:
        violations += list(parsed.tree.recursive_crawl("unparsable"))
    return violations == []


@pytest.mark.parametrize(
    "sql",
    [
        # Hive allows either key=value pairs or bare keys, never a mix.
        "ALTER TABLE t UNSET TBLPROPERTIES ('a' = 'b', 'c');",
        # Hive column definitions have no column constraints.
        "ALTER TABLE t ADD COLUMNS (a STRING NOT NULL);",
        "ALTER TABLE t REPLACE COLUMNS (a STRING PRIMARY KEY);",
        # CHANGE takes plain identifiers, not qualified references.
        "ALTER TABLE t CHANGE a.b c STRING;",
        "ALTER TABLE t CHANGE a b STRING AFTER c.d;",
    ],
)
def test_hive_alter_table_rejects_invalid_clauses(sql):
    """Clauses outside the Hive grammar must not parse."""
    assert not _parses_cleanly(sql)


@pytest.mark.parametrize(
    "sql",
    [
        "ALTER TABLE t UNSET TBLPROPERTIES ('a', 'c');",
        "ALTER TABLE t UNSET TBLPROPERTIES ('a' = 'b', 'c' = 'd');",
        "ALTER TABLE t ADD COLUMNS (a STRING COMMENT 'y' DEFAULT 'x');",
        "ALTER TABLE t CHANGE COLUMN a b STRING COMMENT 'z' AFTER c;",
    ],
)
def test_hive_alter_table_accepts_valid_clauses(sql):
    """Valid Hive clauses parse cleanly."""
    assert _parses_cleanly(sql)
