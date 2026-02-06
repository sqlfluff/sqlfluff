"""Test the OPENJSON alias fix for issue #7442.

This ensures that column references in OPENJSON WITH clauses
are not treated as table column references.
"""

import pytest

from sqlfluff.core.linter.linter import Linter
from sqlfluff.utils.analysis.select import get_select_statement_info


def test_openjson_column_references_excluded():
    """Test that OPENJSON WITH clause columns are not in reference buffer.

    Issue #7442: OPENJSON column references in the WITH clause are schema
    definitions, not actual column references, and should not be treated
    as table references for linting purposes.
    """
    sql = """SELECT t.id, t.name
FROM OPENJSON(@json)
WITH (
    id INT,
    name NVARCHAR(50)
) AS t"""

    linter = Linter(dialect="tsql")
    parsed = linter.parse_string(sql)

    # Make sure it's fully parsable
    assert "unparsable" not in parsed.tree.descendant_type_set

    select_stmt = list(parsed.tree.recursive_crawl("select_statement"))[0]
    select_info = get_select_statement_info(select_stmt, linter.dialect, early_exit=False)

    # The reference buffer should only contain t.id and t.name
    # It should NOT contain @json, id, or name from the OPENJSON WITH clause
    ref_raws = [ref.raw for ref in select_info.reference_buffer]

    # Should have the qualified column references from SELECT
    assert "t.id" in ref_raws
    assert "t.name" in ref_raws

    # Should NOT have the OPENJSON parameter
    assert "@json" not in ref_raws

    # Should NOT have the column definitions from the WITH clause
    assert "id" not in ref_raws or any(r == "id" for r in ref_raws if r == "id")
    # Actually id might appear as t.id, let's check for unqualified id
    unqualified_refs = [ref.raw for ref in select_info.reference_buffer
                        if not ref.is_qualified()]
    assert "id" not in unqualified_refs
    assert "name" not in unqualified_refs


def test_openjson_alias_not_corrupted():
    """Test that sqlfluff fix doesn't corrupt OPENJSON aliases.

    This is a regression test for issue #7442.
    """
    sql = """SELECT t.id, t.name
FROM OPENJSON(@json)
WITH (
    id INT,
    name NVARCHAR(50)
) AS t"""

    linter = Linter(dialect="tsql")
    result = linter.lint_string(sql, fix=True)

    # The fix should NOT add t. prefix to @json, id, or name
    fixed_sql = result.tree.raw

    # Should not have t.@json or t.t.@json
    assert "t.@json" not in fixed_sql

    # Should preserve the AS t alias
    assert "AS t" in fixed_sql

    # The OPENJSON call should still have @json (not corrupted)
    assert "OPENJSON(@json)" in fixed_sql or "OPENJSON (@json)" in fixed_sql
