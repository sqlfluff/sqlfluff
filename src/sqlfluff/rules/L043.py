"""Implementation of Rule L043."""

from sqlfluff.core.parser import WhitespaceSegment, SymbolSegment, KeywordSegment

from sqlfluff.core.rules.base import BaseRule, LintFix, LintResult
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


@document_fix_compatible
class Rule_L043(BaseRule):
    """Unnecessary case when statement. Use the "when" condition itself.

    If a case when else statement returns booleans, we can reduce it to the
    "when" condition.

    | **Anti-pattern**

    .. code-block:: sql

        select
            case
                when fab > 0 then true else false end as is_fab
        from fancy_table

    | **Best practice**
    |   Reduce to "when" condition. Wrap with "coalesce". If necessary, add
    |   a "not" operator at the beginning.

    .. code-block:: sql

        select
            coalesce(fab > 0, false) as is_fab
        from fancy_table

    """

    def _eval(self, segment, **kwargs):
        """Find rule violations and provide fixes.

        0. Look for a case expression
        1. Find the first expression and "then"
        2. Determine if the "then" is followed by a boolean
        3. If so, determine if the first then-bool is followed by an else-bool
        4. If so, delete everything but the first expression
        5a. If then-true-else-false
            * return deletions
            * wrap with coalesce
        5b. If then-false-else-true
            * return deletions
            * add a not condition
            * wrap with parenthesis and coalesce
        """
        # Look for a case expression
        if segment.is_type("case_expression") and segment.segments[0].name == "case":
            # Find the first expression and "then"
            idx = 0
            while segment.segments[idx].name != "then":
                if segment.segments[idx].is_type("expression"):
                    expression_idx = idx
                idx += 1
            # Determine if "then" is followed by a boolean
            then_bool_type = None
            while segment.segments[idx].name not in ["when", "else", "end"]:
                if segment.segments[idx].raw_upper in ["TRUE", "FALSE"]:
                    then_bool_type = segment.segments[idx].raw_upper
                idx += 1
            if then_bool_type:
                # Determine if the first then-bool is followed by an else-bool
                while segment.segments[idx].name != "else":
                    # If the first then-bool is followed by a "WHEN" or "END", exit
                    if segment.segments[idx].name in ["when", "end"]:
                        return None
                    idx += 1  # pragma: no cover
                # Determine if "else" is followed by a boolean
                else_bool_type = None
                while segment.segments[idx].name != "end":
                    if segment.segments[idx].raw_upper in ["TRUE", "FALSE"]:
                        else_bool_type = segment.segments[idx].raw_upper
                    idx += 1
            # If then-bool-else-bool, return fixes
            if (
                then_bool_type is not None
                and else_bool_type is not None
                and then_bool_type != else_bool_type
            ):
                # Generate list of segments to delete -- everything but the
                # first expression.
                delete_segments = []
                for s in segment.segments:
                    if s != segment.segments[expression_idx]:
                        delete_segments.append(s)
                # If then-false, add "not" and space
                edits = []
                if then_bool_type == "FALSE":
                    edits.extend(
                        [
                            KeywordSegment("not"),
                            WhitespaceSegment(),
                        ]
                    )
                # Add coalesce and parenthesis
                edits.extend(
                    [
                        KeywordSegment("coalesce"),
                        SymbolSegment("(", name="start_bracket", type="start_bracket"),
                    ]
                )
                edit_coalesce_target = segment.segments[0]
                fixes = []
                fixes.append(
                    LintFix(
                        "edit",
                        edit_coalesce_target,
                        edits,
                    )
                )
                # Add comma, bool, closing parenthesis
                expression = segment.segments[expression_idx + 1]
                closing_parenthesis = [
                    SymbolSegment(",", name="comma", type="comma"),
                    WhitespaceSegment(),
                    KeywordSegment("false"),
                    SymbolSegment(")", name="end_bracket", type="end_bracket"),
                ]
                fixes.append(
                    LintFix(
                        "edit",
                        expression,
                        closing_parenthesis,
                    )
                )
                # Generate a "delete" action for each segment in
                # delete_segments EXCEPT the one being edited to become a call
                # to "coalesce(". Deleting and editing the same segment has
                # unpredictable behavior.
                fixes += [
                    LintFix("delete", s)
                    for s in delete_segments
                    if s is not edit_coalesce_target
                ]
                return LintResult(
                    anchor=segment.segments[expression_idx],
                    fixes=fixes,
                    description="Case when returns booleans.",
                )
