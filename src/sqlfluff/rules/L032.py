"""Implementation of Rule L032."""
from typing import List, Optional, Tuple
from sqlfluff.core.parser.segments.base import BaseSegment
from sqlfluff.core.parser.segments.raw import (
    CodeSegment,
    KeywordSegment,
    SymbolSegment,
    WhitespaceSegment,
)
from sqlfluff.core.rules.base import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.doc_decorators import document_fix_compatible
import sqlfluff.core.rules.functional.segment_predicates as sp
from sqlfluff.core.rules.functional.segments import Segments
from sqlfluff.core.rules.analysis.select import get_select_statement_info
from sqlfluff.dialects.dialect_ansi import ColumnReferenceSegment


@document_fix_compatible
class Rule_L032(BaseRule):
    """Prefer specifying join keys instead of using ``USING``.

    .. note::
       This rule was taken from the `dbt Style Guide
       <https://github.com/dbt-labs/corp/blob/master/dbt_style_guide.md>`_
       which notes that:

        Certain warehouses have inconsistencies in ``USING``
        results (specifically Snowflake).

       Other users may prefer to disable this rule.

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

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Look for USING in a join clause."""
        segment = context.functional.segment
        parent_stack = context.functional.parent_stack
        # We are not concerned with non join clauses
        if not segment.all(sp.is_type("join_clause")):
            return None

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

        # If we have more than 2 tables we won't try to fix join.
        # TODO: if this is table 2 of 3 it is still fixable
        if len(tables_in_join) > 2:
            return unfixable_result

        parent_select = parent_stack.last(sp.is_type("select_statement")).get()
        if not parent_select:  # pragma: no cover
            return unfixable_result

        select_info = get_select_statement_info(parent_select, context.dialect)
        if not select_info:  # pragma: no cover
            return unfixable_result

        to_delete, insert_after_anchor = _extract_deletion_sequence_and_anchor(
            tables_in_join.last()
        )
        table_a, table_b = select_info.table_aliases
        edit_segments = [
            KeywordSegment(raw="ON"),
            WhitespaceSegment(raw=" "),
        ] + _generate_join_conditions(
            table_a.ref_str,
            table_b.ref_str,
            select_info.using_cols,
        )

        fixes = [
            LintFix.create_before(
                anchor_segment=insert_after_anchor,
                edit_segments=edit_segments,
            ),
            *[LintFix.delete(seg) for seg in to_delete],
        ]
        return LintResult(
            anchor=anchor,
            description=description,
            fixes=fixes,
        )


def _generate_join_conditions(table_a_ref: str, table_b_ref: str, columns: List[str]):
    edit_segments: List[BaseSegment] = []
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


SequenceAndAnchorRes = Tuple[List[BaseSegment], BaseSegment]


def _extract_deletion_sequence_and_anchor(
    join_clause: Segments,
) -> SequenceAndAnchorRes:
    insert_anchor: Optional[BaseSegment] = None
    to_delete: List[BaseSegment] = []
    for seg in join_clause.children():
        if seg.name == "using":
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


def _create_col_reference(table_ref: str, column_name: str):
    segments = [
        CodeSegment(raw=table_ref, name="naked_identifier", type="identifier"),
        SymbolSegment(raw=".", type="symbol", name="dot"),
        CodeSegment(raw=column_name, name="naked_identifier", type="identifier"),
    ]
    return ColumnReferenceSegment(segments=segments, pos_marker=None)
