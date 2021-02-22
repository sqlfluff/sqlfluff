"""Implementation of Rule L043."""

from sqlfluff.core.rules.base import BaseCrawler, LintFix, LintResult
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


@document_fix_compatible
class Rule_L043(BaseCrawler):
    """Use an explicit condition rather than case when statement.

    | **Anti-pattern**

    .. code-block:: sql

        select
            case
                when fab > 0 then true else false end as is_fab
        from fancy_table

    | **Best practice**

    .. code-block:: sql

        select
            fab > 0 as is_fab
        from fancy_table

    """

    def _eval(self, segment, **kwargs):
        """Find rule violations and provide fixes.

        0. Look for a case expression
        1. Find the first expression and "then"
        2. Determine if "then" is followed by a boolean
        3. If so, delete everything but the first expression
        4a. If when-then-true, return deletions
        4b. If when-then-false, return deletions and
            * add a not condition
            * wrap the expression in parenthesis
        """
        if segment.is_type("case_expression"):
            # Find the first expression and "then"
            idx = 0
            while segment.segments[idx].name != "THEN":
                if segment.segments[idx].is_type("expression"):
                    expression_idx = idx
                idx += 1

            # Determine if "then" is followed by a boolean
            while segment.segments[idx].name not in ["WHEN", "ELSE", "END"]:
                if segment.segments[idx].raw_upper in ["TRUE", "FALSE"]:
                    # Delete everything but the first expression
                    fixes = []
                    for s in segment.segments:
                        if s != segment.segments[expression_idx]:
                            fixes.append(LintFix("delete", s))

                    # If then-false, add "not" and wrap expression in parenthesis
                    if segment.segments[idx].raw_upper == "FALSE":
                        not_space_parenthesis = [
                            self.make_keyword(
                                raw="not",
                                pos_marker=segment.get_start_pos_marker(),
                            ),
                            self.make_whitespace(
                                raw=" ",
                                pos_marker=segment.get_start_pos_marker(),
                            ),
                            self.make_symbol(
                                raw="(",
                                pos_marker=segment.get_start_pos_marker(),
                                seg_type="parenthesis",
                            ),
                        ]
                        fixes.append(
                            LintFix(
                                "edit",
                                segment.segments[0],
                                not_space_parenthesis,
                            )
                        )
                        expression = segment.segments[expression_idx + 1]
                        closing_parenthesis = [
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
                idx += 1
            return None
