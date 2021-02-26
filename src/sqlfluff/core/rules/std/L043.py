"""Implementation of Rule L043."""

from sqlfluff.core.rules.base import BaseCrawler, LintFix, LintResult
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


@document_fix_compatible
class Rule_L043(BaseCrawler):
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
        if segment.is_type("case_expression") and segment.segments[0].name == "CASE":
            # Find the first expression and "then"
            idx = 0
            while segment.segments[idx].name != "THEN":
                if segment.segments[idx].is_type("expression"):
                    expression_idx = idx
                idx += 1
            # Determine if "then" is followed by a boolean
            then_bool_type = None
            while segment.segments[idx].name not in ["WHEN", "ELSE", "END"]:
                if segment.segments[idx].raw_upper in ["TRUE", "FALSE"]:
                    then_bool_type = segment.segments[idx].raw_upper
                idx += 1
            if then_bool_type:
                # Determine if the first then-bool is followed by an else-bool
                while segment.segments[idx].name != "ELSE":
                    # If the first then-bool is followed by a "WHEN" or "END", exit
                    if segment.segments[idx].name in ["WHEN", "END"]:
                        return None
                    idx += 1
                # Determine if "else" is followed by a boolean
                else_bool_type = None
                while segment.segments[idx].name != "END":
                    if segment.segments[idx].raw_upper in ["TRUE", "FALSE"]:
                        else_bool_type = segment.segments[idx].raw_upper
                    idx += 1
            # If then-bool-else-bool, return fixes
            if (
                then_bool_type is not None
                and else_bool_type is not None
                and then_bool_type != else_bool_type
            ):
                # Delete everything but the first expression
                fixes = []
                for s in segment.segments:
                    if s != segment.segments[expression_idx]:
                        fixes.append(LintFix("delete", s))
                # If then-false, add "not" and space
                edits = []
                if then_bool_type == "FALSE":
                    not_space = [
                        self.make_keyword(
                            raw="not",
                            pos_marker=segment.get_start_pos_marker(),
                        ),
                        self.make_whitespace(
                            raw=" ",
                            pos_marker=segment.get_start_pos_marker(),
                        ),
                    ]
                    edits.extend(not_space)
                # Add coalesce and parenthesis
                coalesce_parenthesis = [
                    self.make_keyword(
                        raw="coalesce",
                        pos_marker=segment.get_start_pos_marker(),
                    ),
                    self.make_symbol(
                        raw="(",
                        pos_marker=segment.get_start_pos_marker(),
                        seg_type="parenthesis",
                    ),
                ]
                edits.extend(coalesce_parenthesis)
                fixes.append(
                    LintFix(
                        "edit",
                        segment.segments[0],
                        edits,
                    )
                )
                # Add comma, bool, closing parenthesis
                expression = segment.segments[expression_idx + 1]
                closing_parenthesis = [
                    self.make_symbol(
                        raw=",",
                        pos_marker=expression.pos_marker,
                        seg_type="comma",
                    ),
                    self.make_whitespace(
                        raw=" ",
                        pos_marker=expression.pos_marker,
                    ),
                    self.make_keyword(
                        raw="false",
                        pos_marker=expression.pos_marker,
                    ),
                    self.make_symbol(
                        raw=")",
                        pos_marker=expression.pos_marker,
                        seg_type="parenthesis",
                    ),
                ]
                fixes.append(
                    LintFix(
                        "edit",
                        expression,
                        closing_parenthesis,
                    )
                )
                return LintResult(
                    anchor=segment.segments[expression_idx],
                    fixes=fixes,
                    description="Case when returns booleans.",
                )
