"""Implementation of Rule L067."""

from typing import Optional, cast, TypeVar, Type

from sqlfluff.core.parser.segments.base import BaseSegment

from sqlfluff.core.parser.segments.raw import CodeSegment
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
import sqlfluff.core.rules.functional.segment_predicates as sp
from sqlfluff.core.rules.doc_decorators import document_fix_compatible, document_groups


@document_groups
@document_fix_compatible
class Rule_L067(BaseRule):
    """Use ``CAST`` instead of ``CONVERT`` or ``::``.

    **Anti-pattern**

    .. code-block:: sql

        SELECT convert(varchar, 1) AS bar
        FROM foo;

        SELECT 1::varchar AS bar
        FROM foo;

    **Best practice**

    Use ``CAST`` instead.
    ``CAST`` is universally supported

    .. code-block:: sql

        SELECT CAST(1 AS varchar) AS bar,
        FROM foo;

    """

    groups = ("all",)

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Use ``CAST`` instead of ``CONVERT`` or ``::``."""
        # Limit scope to CONVERT and casting_operator
        # CONVERT
        if (
            context.segment.is_type("function")
            and context.segment.get_child("function_name").raw_upper == "CONVERT"
        ):
            # Get the content of CONVERT
            convert_content = context.functional.segment.children(
                sp.is_type("bracketed")
            ).children(
                sp.and_(
                    sp.not_(sp.is_meta()),
                    sp.not_(
                        sp.is_type(
                            "start_bracket", "end_bracket", "whitespace", "newline", "comma",
                        )
                    ),
                )
            )

            # get the expression
            expression = convert_content[1].raw

            # get the data type
            datatype = convert_content[0].raw

            # Create fix to replace ``CONVERT`` with ``CAST``.
            fix = LintFix.replace(
                context.segment,
                [
                    CodeSegment(
                        raw=f"CAST({expression} AS {datatype})",
                    )
                ],
            )

            return LintResult(
                anchor=context.segment,
                fixes=[fix],
                description=f"Use 'CAST' instead of '{context.segment.get_child('function_name').raw_upper}'.",
            )

        # casting_operator
        if (
            context.segment.is_type("cast_expression")
        ):
            # get the datatype and the expression segment
            print(context.segment.type)
            datatype_expression_segment = context.functional.segment.children(
                sp.and_(
                    sp.not_(sp.is_meta()),
                    sp.not_(
                        sp.is_type(
                            "start_bracket", "end_bracket", "whitespace", "newline", "casting_operator",
                        )
                    ),
                )
            )

            # get the expression
            expression = datatype_expression_segment[0].raw

            # get the data type
            datatype = datatype_expression_segment[1].raw

            # create fix to replace ``::`` with ``CAST``.
            fix = LintFix.replace(
                context.segment,
                [
                    CodeSegment(
                        raw=f"CAST({expression} AS {datatype})",
                    )
                ],
            )

            return LintResult(
                anchor=context.segment,
                fixes=[fix],
                description=f"Use 'CAST' instead of '{context.segment.get_child('casting_operator').raw}'.",
            )

        return None
