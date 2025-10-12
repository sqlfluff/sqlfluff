"""Tests for LT01 alias alignment with Jinja templating.

This ensures alignment uses source positions when templated content is present
so that alignment reflects what the user sees in the editor.
"""

from __future__ import annotations

import sqlfluff
from sqlfluff.core.config import FluffConfig


def _count_lt01(results: list[dict]) -> int:
    return sum(1 for r in results if r.get("code") == "LT01")


def test_lt01_alias_alignment_with_jinja_uses_source_positions() -> None:
    """Jinja before alias should not cause excessive padding (align by source)."""
    sql = (
        "select\n"
        "    {{ generate_surrogate_key('test', ['a', 'b', 'c']) }} as test_key,\n"
        "    b as b_col\n"
        "from {{ ref('test') }}\n"
    )

    # First lint should report LT01 (spacing around select + alias alignment).
    cfg = FluffConfig.from_kwargs(dialect="ansi")
    # Inject settings not supported by from_kwargs via child config and update
    cfg._configs["core"]["templater"] = "jinja"
    cfg._configs.setdefault("templater", {}).setdefault("jinja", {}).setdefault(
        "context", {}
    ).update(
        {
            "generate_surrogate_key": lambda *args: "surrogate_key_12345",
            "ref": lambda x: f"my_schema.{x}",
        }
    )
    cfg._configs.setdefault("layout", {}).setdefault("type", {}).setdefault(
        "alias_expression", {}
    ).update(
        {
            "spacing_before": "align",
            "align_within": "select_clause",
            "align_scope": "bracketed",
        }
    )
    initial_results = sqlfluff.lint(sql, config=cfg, rules=["LT01"])
    assert _count_lt01(initial_results) >= 1

    # Apply fixes.
    fixed = sqlfluff.fix(sql, config=cfg, rules=["LT01"])

    # After fixing, there should be no LT01 violations.
    post_results = sqlfluff.lint(fixed, config=cfg, rules=["LT01"])
    assert _count_lt01(post_results) == 0

    # Sanity: alignment should be reasonable. Check that both lines contain ' as '.
    lines = fixed.splitlines()
    assert any(" as " in line for line in lines)

    # Find the two select lines and verify the 'as' columns align by source index.
    select_lines = [line for line in lines if " as " in line]
    assert len(select_lines) >= 2
    first_as_col = select_lines[0].index(" as ")
    second_as_col = select_lines[1].index(" as ")
    assert first_as_col == second_as_col


def test_lt01_alias_alignment_with_jinja_coordinate_space_config_key() -> None:
    """Coordinate space can be set via alignment_coordinate_space config key."""
    sql = "select\n" "    {{ 'templ' }} as a,\n" "    b as bb\n"

    cfg = FluffConfig.from_kwargs(dialect="ansi")
    cfg._configs["core"]["templater"] = "jinja"
    cfg._configs.setdefault("templater", {}).setdefault("jinja", {}).setdefault(
        "context", {}
    )
    # Force templated coordinate space via config key enrichment path
    cfg._configs.setdefault("layout", {}).setdefault("type", {}).setdefault(
        "alias_expression", {}
    ).update(
        {
            "spacing_before": "align",
            "align_within": "select_clause",
            "align_scope": "bracketed",
            "alignment_coordinate_space": "templated",
        }
    )

    fixed = sqlfluff.fix(sql, config=cfg, rules=["LT01"])
    # With templated coordinate space, the second line pads less
    lines = fixed.splitlines()
    assert any(" as " in line for line in lines)
    select_lines = [line for line in lines if " as " in line]
    assert len(select_lines) == 2
    # Check that there is at least some padding before 'as' on second line
    # but not necessarily aligned to the source position of the templated value.
    first_as_col = select_lines[0].index(" as ")
    second_as_col = select_lines[1].index(" as ")
    assert second_as_col <= first_as_col


def test_lt01_alias_alignment_non_rendered_longer_than_template() -> None:
    """Non-rendered column longer than template should align correctly."""
    sql = "select\n" '    {{ "xxx" }} as a,\n' "    fooooooooo as b\n" "from t\n"

    cfg = FluffConfig.from_kwargs(dialect="ansi")
    cfg._configs["core"]["templater"] = "jinja"
    cfg._configs.setdefault("templater", {}).setdefault("jinja", {}).setdefault(
        "context", {}
    )
    cfg._configs.setdefault("layout", {}).setdefault("type", {}).setdefault(
        "alias_expression", {}
    ).update(
        {
            "spacing_before": "align",
            "align_within": "select_clause",
            "align_scope": "bracketed",
        }
    )

    # First lint should report LT01 violations
    initial_results = sqlfluff.lint(sql, config=cfg, rules=["LT01"])
    assert _count_lt01(initial_results) >= 1

    # Apply fixes
    fixed = sqlfluff.fix(sql, config=cfg, rules=["LT01"])

    # After fixing, there should be no LT01 violations
    post_results = sqlfluff.lint(fixed, config=cfg, rules=["LT01"])
    assert _count_lt01(post_results) == 0

    # Verify alignment: both 'as' keywords should align by source position
    lines = fixed.splitlines()
    select_lines = [line for line in lines if " as " in line]
    assert len(select_lines) == 2

    first_as_col = select_lines[0].index(" as ")
    second_as_col = select_lines[1].index(" as ")
    assert first_as_col == second_as_col


def test_lt01_alias_alignment_source_coordinate_space_explicit() -> None:
    """Test explicit source coordinate space setting with templated content."""
    sql = "select\n" "    {{ var1 }} as col1,\n" "    b as col2\n" "from table1\n"

    cfg = FluffConfig.from_kwargs(dialect="ansi")
    cfg._configs["core"]["templater"] = "jinja"
    cfg._configs.setdefault("templater", {}).setdefault("jinja", {}).setdefault(
        "context", {}
    ).update({"var1": "some_value"})

    # Force source coordinate space via config
    cfg._configs.setdefault("layout", {}).setdefault("type", {}).setdefault(
        "alias_expression", {}
    ).update(
        {
            "spacing_before": "align",
            "align_within": "select_clause",
            "align_scope": "bracketed",
            "alignment_coordinate_space": "source",
        }
    )

    fixed = sqlfluff.fix(sql, config=cfg, rules=["LT01"])
    post_results = sqlfluff.lint(fixed, config=cfg, rules=["LT01"])
    assert _count_lt01(post_results) == 0


def test_lt01_alias_alignment_edge_case_no_segments_on_line() -> None:
    """Edge case: no segments found on current line should be handled gracefully."""
    # This creates a scenario that might trigger the edge case
    sql = "select\n" "\n" "    col1 as a,\n" "    col2 as b\n" "from t\n"

    cfg = FluffConfig.from_kwargs(dialect="ansi")
    cfg._configs.setdefault("layout", {}).setdefault("type", {}).setdefault(
        "alias_expression", {}
    ).update(
        {
            "spacing_before": "align",
            "align_within": "select_clause",
            "align_scope": "bracketed",
        }
    )

    # This should handle the edge case gracefully
    fixed = sqlfluff.fix(sql, config=cfg, rules=["LT01"])
    post_results = sqlfluff.lint(fixed, config=cfg, rules=["LT01"])
    # Should not crash and should not produce LT01 violations
    assert isinstance(fixed, str)
    assert _count_lt01(post_results) == 0


def test_lt01_alias_alignment_target_segment_not_found() -> None:
    """Edge case: target segment not found in current line should be handled."""
    # This creates a complex scenario that might trigger the target not found case
    sql = (
        "select\n"
        "    case when 1=1\n"
        "         then col1 end as a,\n"
        "    col2 as b\n"
        "from t\n"
    )

    cfg = FluffConfig.from_kwargs(dialect="ansi")
    cfg._configs.setdefault("layout", {}).setdefault("type", {}).setdefault(
        "alias_expression", {}
    ).update(
        {
            "spacing_before": "align",
            "align_within": "select_clause",
            "align_scope": "bracketed",
        }
    )

    # This should handle the target not found case gracefully
    fixed = sqlfluff.fix(sql, config=cfg, rules=["LT01"])
    post_results = sqlfluff.lint(fixed, config=cfg, rules=["LT01"])
    # Should not crash and should not produce LT01 violations
    assert isinstance(fixed, str)
    assert _count_lt01(post_results) == 0


def test_lt01_alias_alignment_templated_next_segment() -> None:
    """Templated next segment should be detected and aligned by source positions."""
    sql = "select\n" "    col1 as a,\n" "    {{ col2 }} as b\n"

    cfg = FluffConfig.from_kwargs(dialect="ansi")
    cfg._configs["core"]["templater"] = "jinja"
    cfg._configs.setdefault("templater", {}).setdefault("jinja", {}).setdefault(
        "context", {}
    ).update({"col2": "column_two"})
    cfg._configs.setdefault("layout", {}).setdefault("type", {}).setdefault(
        "alias_expression", {}
    ).update(
        {
            "spacing_before": "align",
            "align_within": "select_clause",
            "align_scope": "bracketed",
        }
    )

    # This should trigger the templated content detection for next_seg
    fixed = sqlfluff.fix(sql, config=cfg, rules=["LT01"])
    post_results = sqlfluff.lint(fixed, config=cfg, rules=["LT01"])
    assert _count_lt01(post_results) == 0


def test_lt01_alias_alignment_templated_siblings() -> None:
    """Templated siblings should be detected and aligned by source positions."""
    sql = "select\n" "    {{ col1 }} as a,\n" "    col2 as b,\n" "    {{ col3 }} as c\n"

    cfg = FluffConfig.from_kwargs(dialect="ansi")
    cfg._configs["core"]["templater"] = "jinja"
    cfg._configs.setdefault("templater", {}).setdefault("jinja", {}).setdefault(
        "context", {}
    ).update({"col1": "column_one", "col3": "column_three"})
    cfg._configs.setdefault("layout", {}).setdefault("type", {}).setdefault(
        "alias_expression", {}
    ).update(
        {
            "spacing_before": "align",
            "align_within": "select_clause",
            "align_scope": "bracketed",
        }
    )

    # This should trigger templated content detection for siblings
    fixed = sqlfluff.fix(sql, config=cfg, rules=["LT01"])
    post_results = sqlfluff.lint(fixed, config=cfg, rules=["LT01"])
    assert _count_lt01(post_results) == 0
