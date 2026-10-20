"""Tests the interaction between LT08 and LT15."""

from sqlfluff.core import FluffConfig, Linter


def test_rules_std_LT08_LT15_inserted_copies() -> None:
    """LT15 checks the newline it was given, not an earlier copy of it.

    LT08 inserts the same newline segment twice, so once its fix is applied
    the tree holds two copies which share a uuid, and so are equal.
    """
    cfg = FluffConfig.from_string("""[sqlfluff]
dialect = ansi
rules = LT08, LT15

[sqlfluff:rules:layout.newlines]
maximum_empty_lines_between_statements = 0
""")
    result = Linter(config=cfg).lint_string(
        "with a as (select 1), b as (select 2) select * from a\n", fix=True
    )
    assert ("LT15", 1, 23) in [
        (v.rule_code(), v.line_no, v.line_pos) for v in result.get_violations()
    ]
