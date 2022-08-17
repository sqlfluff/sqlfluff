"""Implementation of Rule L069."""

from typing import Optional

from sqlfluff.core.parser.segments.raw import CodeSegment
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.utils.functional import sp, FunctionalContext
from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
    document_groups,
)


@document_groups
@document_fix_compatible
@document_configuration
class Rule_L069(BaseRule):
    """Use ``CAST`` instead of ``CONVERT`` or ``::``.

    .. note::
        This is only compatible with 2-arguments CONVERT as
        some dialects allow an optional 3rd argument e.g TSQL,
        which cannot be rewritten into CAST.
        This rule is disabled by default for Teradata because it supports different
        type casting apart from CONVERT and ::
        e.g DATE '2007-01-01', '9999-12-31' (DATE).

    **Anti-pattern**

    Using CONVERT or :: instead of CAST when ``allow_non_standard_type_casting``
    config is set to ``False`` (default).

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
    config_keywords = ["allow_non_standard_type_casting"]
    crawl_behaviour = SegmentSeekerCrawler({"function", "cast_expression"})

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Use ``CAST`` instead of ``CONVERT`` or ``::``."""
        # Config type hints
        self.allow_non_standard_type_casting: bool

        # Rule disabled for teradata.
        if context.dialect.name == "teradata":
            return None

        if not self.allow_non_standard_type_casting:
            # Limit scope to CONVERT and casting_operator(::)
            # CONVERT
            if (
                context.segment.is_type("function")
                and context.segment.get_child("function_name").raw_upper == "CONVERT"
            ):
                # Get the content of CONVERT
                convert_content = (
                    FunctionalContext(context)
                    .segment.children(sp.is_type("bracketed"))
                    .children(
                        sp.and_(
                            sp.not_(sp.is_meta()),
                            sp.not_(
                                sp.is_type(
                                    "start_bracket",
                                    "end_bracket",
                                    "whitespace",
                                    "newline",
                                    "comma",
                                )
                            ),
                        )
                    )
                )

                # we only care about 2-arguments convert
                # some dialects allow an optional 3rd argument e.g TSQL
                # which cannot be rewritten into CAST
                if len(convert_content) > 2:
                    return None

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
                    description=f"Use 'CAST' instead of \n"
                    f"'{context.segment.get_child('function_name').raw_upper}'.",
                )

            # casting_operator(::)
            if context.segment.is_type("cast_expression"):
                # get the expression and the datatype segment
                expression_datatype_segment = FunctionalContext(
                    context
                ).segment.children(
                    sp.and_(
                        sp.not_(sp.is_meta()),
                        sp.not_(
                            sp.is_type(
                                "start_bracket",
                                "end_bracket",
                                "whitespace",
                                "newline",
                                "casting_operator",
                            )
                        ),
                    )
                )

                # we can have multicast e.g 1::int::text
                # in that case, we need to introduce multiple CAST()
                # start off new_segment as the expression
                new_segment = expression_datatype_segment[0].raw

                for datatype_level in range(len(expression_datatype_segment[1:])):
                    # skip the first element(the expression)
                    datatype_level = datatype_level + 1
                    # update new_segment to include datatype
                    # as well as accommodate multicast
                    new_datatype = expression_datatype_segment[datatype_level].raw
                    new_segment = f"CAST({new_segment} AS {new_datatype})"

                # create fix to replace ``::`` with ``CAST``.
                fix = LintFix.replace(
                    context.segment,
                    [
                        CodeSegment(
                            raw=new_segment,
                        )
                    ],
                )

                return LintResult(
                    anchor=context.segment,
                    fixes=[fix],
                    description=f"Use 'CAST' instead of \n"
                    f"'{context.segment.get_child('casting_operator').raw}'.",
                )

            return None
        return None
