"""Tests for LT01 alias alignment with Jinja templating.

This ensures alignment uses source positions when templated content is present
so that alignment reflects what the user sees in the editor.
"""

from __future__ import annotations

from sqlfluff.core.config import FluffConfig
import sqlfluff


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
    select_lines = [l for l in lines if " as " in l]
    assert len(select_lines) >= 2
    first_as_col = select_lines[0].index(" as ")
    second_as_col = select_lines[1].index(" as ")
    assert first_as_col == second_as_col


