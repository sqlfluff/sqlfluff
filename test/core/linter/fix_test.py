"""Test routines for fixing errors."""

import logging

import pytest

from sqlfluff.core import Linter
from sqlfluff.core.config import FluffConfig
from sqlfluff.core.linter.fix import compute_anchor_edit_info
from sqlfluff.core.linter.patch import (
    FixPatch,
    generate_source_patches,
    merge_source_patches,
)
from sqlfluff.core.parser.markers import PositionMarker
from sqlfluff.core.parser.segments import (
    BaseSegment,
    RawSegment,
    TemplateSegment,
)
from sqlfluff.core.parser.segments.raw import SourceFix
from sqlfluff.core.rules.fix import LintFix
from sqlfluff.core.templaters import RawFileSlice, TemplatedFile
from sqlfluff.core.templaters.base import TemplatedFileSlice


@pytest.fixture(scope="module")
def raw_segments(generate_test_segments):
    """Construct a list of raw segments as a fixture."""
    return generate_test_segments(["foobar", ".barfoo"])


def test__rules_base_segments_compute_anchor_edit_info(raw_segments):
    """Test BaseSegment.compute_anchor_edit_info()."""
    # Construct a fix buffer, intentionally with:
    # - one duplicate.
    # - two different incompatible fixes on the same segment.
    fixes = [
        LintFix.replace(raw_segments[0], [raw_segments[0].edit(raw="a")]),
        LintFix.replace(raw_segments[0], [raw_segments[0].edit(raw="a")]),
        LintFix.replace(raw_segments[0], [raw_segments[0].edit(raw="b")]),
    ]
    anchor_info_dict = compute_anchor_edit_info(fixes)
    # Check the target segment is the only key we have.
    assert list(anchor_info_dict.keys()) == [raw_segments[0].uuid]
    anchor_info = anchor_info_dict[raw_segments[0].uuid]
    # Check that the duplicate as been deduplicated.
    # i.e. this isn't 3.
    assert anchor_info.replace == 2
    # Check the fixes themselves.
    # NOTE: There's no duplicated first fix.
    assert anchor_info.fixes == [
        LintFix.replace(raw_segments[0], [raw_segments[0].edit(raw="a")]),
        LintFix.replace(raw_segments[0], [raw_segments[0].edit(raw="b")]),
    ]
    # Check the first replace
    assert anchor_info._first_replace == LintFix.replace(
        raw_segments[0], [raw_segments[0].edit(raw="a")]
    )


templated_file_1 = TemplatedFile.from_string("abc")
templated_file_2 = TemplatedFile(
    "{# blah #}{{ foo }}bc",
    "<testing>",
    "abc",
    [
        TemplatedFileSlice("comment", slice(0, 10), slice(0, 0)),
        TemplatedFileSlice("templated", slice(10, 19), slice(0, 1)),
        TemplatedFileSlice("literal", slice(19, 21), slice(1, 3)),
    ],
    [
        RawFileSlice("{# blah #}", "comment", 0),
        RawFileSlice("{{ foo }}", "templated", 10),
        RawFileSlice("bc", "literal", 19),
    ],
)


@pytest.mark.parametrize(
    "tree,templated_file,expected_result",
    [
        # Trivial example
        (
            RawSegment(
                "abc",
                PositionMarker(slice(0, 3), slice(0, 3), templated_file_1),
                "code",
            ),
            templated_file_1,
            [],
        ),
        # Simple literal edit example
        (
            RawSegment(
                "abz",
                PositionMarker(slice(0, 3), slice(0, 3), templated_file_1),
                "code",
            ),
            templated_file_1,
            [FixPatch(slice(0, 3), "abz", "literal", slice(0, 3), "abc", "abc")],
        ),
        # Nested literal edit example
        (
            BaseSegment(
                [
                    RawSegment(
                        "a",
                        PositionMarker(slice(0, 1), slice(0, 1), templated_file_1),
                        "code",
                    ),
                    RawSegment(
                        "b",
                        PositionMarker(slice(1, 2), slice(1, 2), templated_file_1),
                        "code",
                    ),
                    RawSegment(
                        "z",
                        PositionMarker(slice(2, 3), slice(2, 3), templated_file_1),
                        "code",
                    ),
                ]
            ),
            templated_file_1,
            [FixPatch(slice(0, 3), "abz", "literal", slice(0, 3), "abc", "abc")],
        ),
        # More complicated templating example
        (
            BaseSegment(
                [
                    TemplateSegment(
                        PositionMarker(slice(0, 10), slice(0, 0), templated_file_2),
                        "{# blah #}",
                        "comment",
                    ),
                    RawSegment(
                        "a",
                        PositionMarker(slice(10, 20), slice(0, 1), templated_file_2),
                        "code",
                    ),
                    RawSegment(
                        "b",
                        PositionMarker(slice(19, 20), slice(1, 2), templated_file_2),
                        "code",
                    ),
                    RawSegment(
                        "z",
                        PositionMarker(slice(20, 21), slice(2, 3), templated_file_2),
                        "code",
                    ),
                ]
            ),
            templated_file_2,
            [FixPatch(slice(2, 3), "z", "literal", slice(20, 21), "c", "c")],
        ),
        # Templating example with fixes
        (
            BaseSegment(
                [
                    TemplateSegment(
                        PositionMarker(slice(0, 10), slice(0, 0), templated_file_2),
                        "{# blah #}",
                        "comment",
                        source_fixes=[
                            SourceFix("{# fixed #}", slice(0, 10), slice(0, 0))
                        ],
                    ),
                    RawSegment(
                        "a",
                        PositionMarker(slice(10, 19), slice(0, 1), templated_file_2),
                        "code",
                        source_fixes=[
                            SourceFix("{{ bar }}", slice(10, 19), slice(0, 1))
                        ],
                    ),
                    RawSegment(
                        "b",
                        PositionMarker(slice(19, 20), slice(1, 2), templated_file_2),
                        "code",
                    ),
                    RawSegment(
                        "z",
                        PositionMarker(slice(20, 21), slice(2, 3), templated_file_2),
                        "code",
                    ),
                ]
            ),
            templated_file_2,
            [
                FixPatch(
                    slice(0, 0), "{# fixed #}", "source", slice(0, 10), "", "{# blah #}"
                ),
                FixPatch(
                    slice(0, 1), "{{ bar }}", "source", slice(10, 19), "a", "{{ foo }}"
                ),
                FixPatch(slice(2, 3), "z", "literal", slice(20, 21), "c", "c"),
            ],
        ),
    ],
)
def test__fix__generate_source_patches(tree, templated_file, expected_result, caplog):
    """Test generate_source_patches.

    This is part of fix_string().
    """
    with caplog.at_level(logging.DEBUG, logger="sqlfluff.linter"):
        result = generate_source_patches(tree, templated_file)
    assert result == expected_result


def test__fix__jinja_empty_rendering_placeholder_adjacent_to_quotes(caplog):
    """Regression test for empty Jinja placeholders inside quoted literals.

    This covers the case where ``{{ foo.bar }}`` renders to an empty string and
    appears adjacent to quote characters, while a fix (LT02 indentation) is
    being applied elsewhere in the statement.
    """
    sql = "SELECT\n  '{{ foo.bar }}'\nFROM baz\n"
    config = FluffConfig(
        overrides={
            "dialect": "ansi",
            "rules": "LT02",
            "templater": "jinja",
            # Ensure the expression renders to an empty string.
            "templater.jinja.context.foo": {"bar": ""},
            "templater.jinja.context.bar": "",
        }
    )
    linter = Linter(config=config)

    with caplog.at_level(logging.WARNING, logger="sqlfluff.linter"):
        linted_file = linter.lint_string(sql, fix=True)
        fixed_sql, changed = linted_file.fix_string()

    assert changed
    assert fixed_sql == "SELECT\n    '{{ foo.bar }}'\nFROM baz\n"
    assert "Skipping edit patch on uncertain templated section" not in caplog.text


def test__fix__jinja_non_empty_context_adjacent_to_quotes(caplog):
    """Regression test for quoted templated literals with non-empty context."""
    sql = "SELECT\n  '{{ foo.bar }}'\nFROM baz\n"
    config = FluffConfig(
        overrides={
            "dialect": "ansi",
            "rules": "LT02",
            "templater": "jinja",
            "templater.jinja.context.foo": {"bar": "bar"},
            "templater.jinja.context.bar": "bar",
        }
    )
    linter = Linter(config=config)

    with caplog.at_level(logging.WARNING, logger="sqlfluff.linter"):
        linted_file = linter.lint_string(sql, fix=True)
        fixed_sql, changed = linted_file.fix_string()

    assert changed
    assert fixed_sql == "SELECT\n    '{{ foo.bar }}'\nFROM baz\n"
    assert "Skipping edit patch on uncertain templated section" not in caplog.text


def test__fix__jinja_dbt_var_subscript_allows_layout_fix():
    """Regression test for dbt `var()` placeholders used with subscripts."""
    sql = "select {{ var('123')['123'] }} ,1/2 as d from d\n"
    config = FluffConfig.from_string(
        "[sqlfluff]\n"
        "dialect = snowflake\n"
        "rules = LT01\n"
        "templater = jinja\n"
        "[sqlfluff:templater:jinja]\n"
        "apply_dbt_builtins = True\n"
    )
    linter = Linter(config=config)

    linted_file = linter.lint_string(sql, fname="test.sql", fix=True)
    fixed_sql, changed = linted_file.fix_string()

    assert changed
    assert not any(v.rule_code() == "PRS" for v in linted_file.get_violations())
    assert fixed_sql == "select {{ var('123')['123'] }}, 1 / 2 as d from d\n"


def test__fix__warning_only_violations_are_still_fixed(tmp_path):
    """Test that warning-level violations are fixed even without errors.

    Regression test for https://github.com/sqlfluff/sqlfluff/issues/7101.
    When all fixable violations are configured as warnings (via the
    ``warnings`` config), ``persist_tree`` should still apply the fixes
    rather than skipping the file.
    """
    # LT02 = incorrect indentation.  Configure it as a warning.
    sql = "SELECT a\nFROM\n        foo;\n"
    expected_fixed = "SELECT a\nFROM\n    foo;\n"
    config = FluffConfig(
        overrides={
            "dialect": "ansi",
            "rules": "LT02",
            "warnings": "LT02",
        }
    )
    linter = Linter(config=config)
    linted_file = linter.lint_string(sql, fix=True)

    # The violation should be present but marked as a warning.
    all_violations = linted_file.get_violations(filter_warning=False)
    assert any(v.warning for v in all_violations), (
        "Expected at least one warning-level violation"
    )

    # fix_string should produce the corrected SQL.
    fixed_sql, changed = linted_file.fix_string()
    assert changed
    assert fixed_sql == expected_fixed

    # persist_tree should detect the fixable warning and write it out.
    sql_file = tmp_path / "test.sql"
    sql_file.write_text(sql)
    linted_file_on_disk = linter.lint_string(sql, fname=str(sql_file), fix=True)
    success = linted_file_on_disk.persist_tree()
    assert success
    assert sql_file.read_text() == expected_fixed


def test__fix__warning_and_error_violations_both_fixed(tmp_path):
    """When a file has both warning and error violations, both are fixed.

    Companion to the warning-only test above: make sure mixed severity
    still works after the change.
    """
    # LT02 = indentation (warning), CP01 = capitalisation (error).
    sql = "SELECT a\nfrom\n        foo;\n"
    expected_fixed = "SELECT a\nFROM\n    foo;\n"
    config = FluffConfig(
        overrides={
            "dialect": "ansi",
            "rules": "LT02,CP01",
            "warnings": "LT02",
        }
    )
    linter = Linter(config=config)

    sql_file = tmp_path / "test.sql"
    sql_file.write_text(sql)
    linted_file = linter.lint_string(sql, fname=str(sql_file), fix=True)
    success = linted_file.persist_tree()
    assert success
    assert sql_file.read_text() == expected_fixed


def test__fix__merge_source_patches_dedupes_and_skips_conflicts():
    """Cross-variant patch merging should keep only safe source edits."""
    patch_a = FixPatch(slice(1, 2), "A", "literal", slice(1, 2), "b", "b")
    patch_a_dup = FixPatch(slice(1, 2), "A", "literal", slice(1, 2), "b", "b")
    patch_b = FixPatch(slice(3, 4), "B", "literal", slice(3, 4), "d", "d")
    conflicting_patch = FixPatch(slice(3, 4), "C", "literal", slice(3, 4), "d", "d")

    assert merge_source_patches(
        [[patch_a, patch_b], [patch_a_dup, conflicting_patch]]
    ) == [patch_a, patch_b]


def test__fix__merge_source_patches_skips_conflicting_insertions_at_same_point():
    """Insert-only patches at the same source point should conflict."""
    first_insertion = FixPatch(
        slice(2, 2),
        "A",
        "mid_point",
        slice(2, 2),
        "",
        "",
    )
    conflicting_insertion = FixPatch(
        slice(5, 5),
        "B",
        "mid_point",
        slice(2, 2, 1),
        "",
        "",
    )

    assert merge_source_patches(
        [[first_insertion], [conflicting_insertion]]
    ) == [first_insertion]
