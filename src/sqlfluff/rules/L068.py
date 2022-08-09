"""Implementation of Rule L068."""

from typing import List, Optional

from sqlfluff.core.parser import WhitespaceSegment

from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules.base import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
    document_groups,
)
import sqlfluff.core.rules.functional.segment_predicates as sp


@document_groups
@document_configuration
@document_fix_compatible
class Rule_L068(BaseRule):
    """The brackets should stand at the same line with from/as/join keywords.
    The ending brackets followed by as keyword should stand at the beginning
    of a new line.

    **Anti-pattern**

    Opening bracket following from keyword takes a new line,
    and as clause at the end takes a new line instead of following end bracket

    .. code-block:: sql
        :force:

        select
            A.something
        from
        (select B from Table1 group by 1)
        as A



    **Best practice**

    Opening bracket following after from keywords with no newline, and ending bracket
    followed by as clause with no newline.

    .. code-block:: sql
        :force:

        select
            A.something
        from (select B from Table1 group by 1) as A

    """
    groups = ("all",)

    def _eval(self, context: RuleContext):

        results: List[LintResult] = []
        children = context.functional.segment.children()

        # check whether from clause contains brackets
        if context.segment.is_type('from_clause'):

            from_expressions = children.select(sp.is_type('from_expression'))
            from_elements = from_expressions.children(
                sp.is_type('from_expression_element')
            )

            # check whether the from clause only contain one expression
            # and it's bracketed
            if len(from_expressions) == 1 and len(from_elements) == 1:

                # if the from element contains subquery, the whole bracket would be
                # parsed as a table expression
                table_expressions = from_elements.children().select(
                    sp.is_type('table_expression')
                )
                if (
                    (
                        table_expressions and
                        table_expressions.children(sp.is_type('bracketed'))
                    ) or
                        from_elements.children(sp.is_type('bracketed'))
                ):

                    # find the newline before opening bracket
                    preceeding_newlines = children.reversed().select(
                        select_if=sp.is_type('newline'),
                        loop_while=sp.or_(
                            sp.is_type('newline'),
                            sp.is_type('whitespace'),
                            sp.is_meta()),
                        start_seg=from_expressions.get()
                    )

                    # find the white space before opening bracket
                    preceeding_whitespaces = children.reversed().select(
                        select_if=sp.is_type('whitespace'),
                        loop_while=sp.or_(sp.is_type('whitespace'), sp.is_meta()),
                        start_seg=from_expressions.get()
                    )

                    # sometimes the white space is in the from expression
                    preceeding_whitespaces += from_expressions.children().select(
                        select_if=sp.is_type('whitespace'),
                        stop_seg=from_elements.get()
                    )
                    if (
                        preceeding_newlines or (
                            preceeding_whitespaces and (
                                len(preceeding_whitespaces) > 1 or
                                preceeding_whitespaces[0].matched_length > 1
                            )
                        )
                    ):
                        results.append(
                            LintResult(
                                anchor=from_expressions.get(),
                                description=(
                                    (
                                        "The opening brackets after from keywords should "
                                        "stand at the end of the line. Extra newline or "
                                        "whitespace found before opening bracket."
                                    )
                                    
                                ),
                                fixes=_generate_fixes(
                                    anchor=from_expressions.get(),
                                    whitespace_segments=preceeding_whitespaces,
                                    newline_segments=preceeding_newlines
                                )
                            )
                        )

        # Check whether as clause is connected with brackets
        # With AS clause would be handled by L018 and L023.
        # Here only consider as at the end like (  ) as ~.
        if children.any(sp.is_type('alias_expression')):
            alias_exp = children.first(sp.is_type('alias_expression'))
            preceeding_code = children.reversed().select(
                start_seg=alias_exp.get()
            ).first(sp.is_code())
            if preceeding_code and (
                preceeding_code[0].is_type('bracketed') or (
                    preceeding_code[0].is_type('table_expression') and
                    preceeding_code.children(sp.is_type('bracketed'))
                )
            ):
                preceeding_newlines = children.select(
                    select_if=sp.is_type('newline'),
                    start_seg=preceeding_code.get(),
                    stop_seg=alias_exp.get()
                )
                preceeding_whitespaces = children.select(
                    select_if=sp.is_type('whitespace'),
                    start_seg=preceeding_code.get(),
                    stop_seg=alias_exp.get()
                )
                if preceeding_newlines:
                    results.append(
                        LintResult(
                            anchor=alias_exp.get(),
                            description=(
                                (
                                    "The ending brackets followed by as keywords should "
                                    "stand at the beginning of the line. Extra newline "
                                    "found after ending bracket."
                                )
                            ),
                            fixes=_generate_fixes(
                                anchor=alias_exp.get(),
                                whitespace_segments=preceeding_whitespaces,
                                newline_segments=preceeding_newlines
                            )
                        )
                    )

        # Check newline in join clause
        if context.segment.is_type('join_clause'):
            bracket = children.select(
                sp.is_type('from_expression_element')
            ).children(
                sp.is_type('table_expression')
            ).children(sp.is_type('bracketed'))
            if bracket:
                from_expression_element = children.select(
                    sp.is_type('from_expression_element')
                ).first().get()
                preceeding_code = children.reversed().select(
                    start_seg=from_expression_element
                ).first(sp.is_code())
                if preceeding_code:
                    preceeding_newline = children.select(
                        select_if=sp.is_type('newline'),
                        start_seg=preceeding_code.get(),
                        stop_seg=from_expression_element
                    )
                    preceeding_whitespace = children.select(
                        select_if=sp.is_type('whitespace'),
                        start_seg=preceeding_code.get(),
                        stop_seg=from_expression_element
                    )
                    if (
                        preceeding_newline or (
                            preceeding_whitespace and (
                                len(preceeding_whitespace) > 1 or
                                preceeding_whitespace[0].matched_length > 1
                            )
                        )
                    ):
                        results.append(
                            LintResult(
                                anchor=from_expression_element,
                                description=(
                                    (
                                        "The opening/ending brackets with join keywords should "
                                        "stand at the same line. Extra newline found."
                                    )
                                ),
                                fixes=_generate_fixes(
                                    anchor=from_expression_element,
                                    whitespace_segments=preceeding_whitespace,
                                    newline_segments=preceeding_newline
                                )
                            )
                        )

        if results:
            return results


def _generate_fixes(
    anchor: BaseSegment,
    whitespace_segments: BaseSegment,
    newline_segments: BaseSegment
) -> Optional[List[LintFix]]:

    fixes = []
    if newline_segments:
        for newline_segment in newline_segments:
            fixes.append(
                LintFix.delete(newline_segment)
            )
    # The trailing white space could have more than one
    if whitespace_segments:
        for whitespace_segment in whitespace_segments:
            fixes.append(
                LintFix.delete(whitespace_segment)
            )
    # Leave only one white space here
    fixes.append(
        LintFix.create_before(
            anchor_segment=anchor,
            edit_segments=[WhitespaceSegment(raw=" ")]
        )
    )

    return fixes
