"""Implementation of Rule ST07."""

from typing import Optional

from sqlfluff.core.dialects.common import iter_raw_references
from sqlfluff.core.parser import (
    BaseSegment,
    IdentifierSegment,
    KeywordSegment,
    SymbolSegment,
    WhitespaceSegment,
)
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.dialects.dialect_ansi import ColumnReferenceSegment
from sqlfluff.utils.analysis.select import get_select_statement_info
from sqlfluff.utils.functional import FunctionalContext, Segments, sp


class Rule_ST07(BaseRule):
    """Prefer specifying join keys instead of using ``USING``.

    .. note::
       This rule was originally taken from the `dbt Style Guide
       <https://github.com/dbt-labs/corp/blob/ main/dbt_style_guide.md>`_
       which notes that:

        Certain warehouses have inconsistencies in ``USING``
        results (specifically Snowflake).

       In fact `dbt removed it from their style guide in February 2022
       <https://github.com/dbt-labs/corp/pull/58>`_. However, some like the
       rule, so for now we will keep it in SQLFluff, but encourage those that
       do not find value in the rule, to turn it off.

    .. note::

       This rule is disabled for ClickHouse as it supports ``USING`` without
       brackets which this rule does not support.

    **Anti-pattern**

    .. code-block:: sql

        SELECT
            table_a.field_1,
            table_b.field_2
        FROM
            table_a
        INNER JOIN table_b USING (id)

    **Best practice**

    Specify the keys directly

    .. code-block:: sql

        SELECT
            table_a.field_1,
            table_b.field_2
        FROM
            table_a
        INNER JOIN table_b
            ON table_a.id = table_b.id

    """

    name = "structure.using"
    aliases = ("L032",)
    groups: tuple[str, ...] = ("all", "structure")
    crawl_behaviour = SegmentSeekerCrawler({"join_clause"})
    is_fix_compatible = True
    _dialects_disabled_by_default = [
        "clickhouse",
    ]

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        if context.dialect.name in self._dialects_disabled_by_default:
            return LintResult()

        """Look for USING in a join clause."""
        segment = FunctionalContext(context).segment
        parent_stack = FunctionalContext(context).parent_stack
        # We are not concerned with non join clauses
        assert context.segment.is_type("join_clause")

        using_anchor = segment.children(sp.is_keyword("using")).first()
        # If there is no evidence of a USING then we exit
        if len(using_anchor) == 0:
            return None

        anchor = using_anchor.get()
        description = "Found USING statement. Expected only ON statements."
        # All returns from here out will be some form of linting error.
        # we prepare the variable here
        unfixable_result = LintResult(
            anchor=anchor,
            description=description,
        )

        tables_in_join = parent_stack.last().children(
            sp.is_type("join_clause", "from_expression_element")
        )

        # We can only safely fix the first join clause
        if segment.get(0) != tables_in_join.get(1):
            return unfixable_result

        parent_select = parent_stack.last(sp.is_type("select_statement")).get()
        if not parent_select:  # pragma: no cover
            return unfixable_result

        select_info = get_select_statement_info(parent_select, context.dialect)
        table_aliases = [
            ta
            for ta in (select_info.table_aliases if select_info else [])
            if ta.ref_str
        ]
        if len(table_aliases) < 2:
            return unfixable_result

        using_col_segments = _extract_cols_from_using(segment, using_anchor)
        using_cols = [seg.raw for seg in using_col_segments]

        # A USING join de-duplicates the join columns, so any reference whose
        # leading identifier is a USING column -- a bare ``field_1`` in the
        # SELECT clause, or a struct access like ``field_1.nested_field`` --
        # relies on that de-duplication. Rewriting to an ON condition would
        # make such references ambiguous and produce invalid SQL, so flag the
        # USING clause but leave it unfixable. Names are compared using the
        # dialect's identifier normalization (which respects quoting and
        # case-folding) rather than a raw upper-case; this also stays
        # conservative when a USING column name happens to match a table
        # alias (a ``field_1.nested_field`` struct access is then still
        # treated as unfixable rather than assumed to be ``table.column``).
        # https://github.com/sqlfluff/sqlfluff/issues/7230
        using_cols_normalized = {seg.raw_normalized() for seg in using_col_segments}
        if select_info:
            for ref in select_info.reference_buffer:
                parts = list(iter_raw_references(ref, context.dialect.name))
                if not parts:  # pragma: no cover
                    continue
                if parts[0].segments[0].raw_normalized() in using_cols_normalized:
                    return unfixable_result

        to_delete, insert_after_anchor = _extract_deletion_sequence_and_anchor(segment)

        # This join connects the base table of its from_expression with the
        # table joined here -- not necessarily the SELECT's first two tables,
        # which diverge when a comma-join precedes this USING join.
        alias_by_element = {
            ta.from_expression_element.uuid: ta
            for ta in table_aliases
            if ta.from_expression_element is not None
        }
        left_element = tables_in_join.get(0)
        right_element = segment.children(sp.is_type("from_expression_element")).get(0)
        table_a = alias_by_element.get(left_element.uuid) if left_element else None
        table_b = alias_by_element.get(right_element.uuid) if right_element else None
        if table_a is None or table_b is None:  # pragma: no cover
            return unfixable_result
        edit_segments = [
            KeywordSegment(raw="ON"),
            WhitespaceSegment(raw=" "),
        ] + _generate_join_conditions(
            table_a.ref_str,
            table_b.ref_str,
            using_cols,
        )

        assert table_a.segment
        assert table_b.segment
        fixes = [
            LintFix.create_before(
                anchor_segment=insert_after_anchor,
                source=[table_a.segment, table_b.segment],
                edit_segments=edit_segments,
            ),
            *[LintFix.delete(seg) for seg in to_delete],
        ]
        return LintResult(
            anchor=anchor,
            description=description,
            fixes=fixes,
        )


def _extract_cols_from_using(join_clause: Segments, using_segs: Segments) -> Segments:
    # First bracket after the USING keyword, then find ids
    return (
        join_clause.children()
        .select(start_seg=using_segs[0], select_if=sp.is_type("bracketed"))
        .first()
        .children(sp.is_type("identifier"))
    )


def _generate_join_conditions(
    table_a_ref: str, table_b_ref: str, columns: list[str]
) -> list[BaseSegment]:
    edit_segments: list[BaseSegment] = []
    for col in columns:
        edit_segments = edit_segments + [
            _create_col_reference(
                table_a_ref,
                col,
            ),
            WhitespaceSegment(raw=" "),
            SymbolSegment(raw="="),
            WhitespaceSegment(raw=" "),
            _create_col_reference(
                table_b_ref,
                col,
            ),
            WhitespaceSegment(raw=" "),
            KeywordSegment(raw="AND"),
            WhitespaceSegment(raw=" "),
        ]

    # Trim the " " "AND" " " at the end
    return edit_segments[:-3]


SequenceAndAnchorRes = tuple[list[BaseSegment], BaseSegment]


def _extract_deletion_sequence_and_anchor(
    join_clause: Segments,
) -> SequenceAndAnchorRes:
    insert_anchor: Optional[BaseSegment] = None
    to_delete: list[BaseSegment] = []
    for seg in join_clause.children():
        if seg.raw_upper == "USING":
            # Start collecting once we hit USING
            to_delete.append(seg)
            continue

        if len(to_delete) == 0:
            # Skip if we haven't started collecting
            continue

        if to_delete[-1].is_type("bracketed"):
            # terminate when we hit the brackets
            insert_anchor = seg
            break

        to_delete.append(seg)

    assert insert_anchor, "Insert Anchor must be present at this point"
    return to_delete, insert_anchor


def _create_col_reference(table_ref: str, column_name: str) -> ColumnReferenceSegment:
    segments = (
        IdentifierSegment(raw=table_ref, type="naked_identifier"),
        SymbolSegment(raw=".", type="symbol"),
        IdentifierSegment(raw=column_name, type="naked_identifier"),
    )
    return ColumnReferenceSegment(segments=segments, pos_marker=None)
