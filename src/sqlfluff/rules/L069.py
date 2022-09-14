"""Implementation of Rule L069."""

from typing import Optional, List

from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.utils.functional import sp, FunctionalContext, Segments

from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
    document_groups,
)
from sqlfluff.core.parser import (
    WhitespaceSegment,
    SymbolSegment,
    KeywordSegment,
    BaseSegment,
)


@document_groups
@document_fix_compatible
@document_configuration
class Rule_L069(BaseRule):
    """Enforce consistent type casting style.

    .. note::
        This is only compatible with 2-arguments CONVERT as
        some dialects allow an optional 3rd argument e.g TSQL,
        which cannot be rewritten into CAST.
        This rule is disabled by default for Teradata because it supports different
        type casting apart from CONVERT and ::
        e.g DATE '2007-01-01', '9999-12-31' (DATE).

    **Anti-pattern**

    Using mixture of CONVERT, :: and CAST when ``preferred_type_casting_style``
    config is set to ``consistent`` (default).

    .. code-block:: sql

        SELECT
            CONVERT(int, 1) AS bar,
            100::int::text,
            CAST(10 AS text) AS coo
        FROM foo;

    **Best practice**

    Use consistent type casting style.

    .. code-block:: sql

        SELECT
            CAST(1 AS int) AS bar,
            CAST(CAST(100 AS int) AS text),
            CAST(10 AS text) AS coo
        FROM foo;

    """

    groups = ("all",)
    config_keywords = ["preferred_type_casting_style"]
    crawl_behaviour = SegmentSeekerCrawler({"function", "cast_expression"})

    @staticmethod
    def _get_children(segments: Segments) -> Segments:
        return segments.children(
            sp.and_(
                sp.not_(sp.is_meta()),
                sp.not_(
                    sp.is_type(
                        "start_bracket",
                        "end_bracket",
                        "whitespace",
                        "newline",
                        "casting_operator",
                        "comma",
                        "keyword",
                    )
                ),
            )
        )

    @staticmethod
    def _cast_fix_list(
        context: RuleContext,
        cast_arg_1: BaseSegment,
        cast_arg_2: BaseSegment,
        later_types=None,
    ) -> List[LintFix]:
        """Generate list of fixes to convert CONVERT and ShortHandCast to CAST."""
        # Add cast and opening parenthesis.
        edits = [
            KeywordSegment("cast"),
            SymbolSegment("(", type="start_bracket"),
            cast_arg_1,
            WhitespaceSegment(),
            KeywordSegment("as"),
            WhitespaceSegment(),
            cast_arg_2,
            SymbolSegment(")", type="end_bracket"),
        ]

        if later_types:
            pre_edits: List[BaseSegment] = [
                KeywordSegment("cast"),
                SymbolSegment("(", type="start_bracket"),
            ]
            in_edits: List[BaseSegment] = [
                WhitespaceSegment(),
                KeywordSegment("as"),
                WhitespaceSegment(),
            ]
            post_edits: List[BaseSegment] = [
                SymbolSegment(")", type="end_bracket"),
            ]
            for _type in later_types:
                edits = pre_edits + edits + in_edits + [_type] + post_edits

        fixes = [
            LintFix.replace(
                context.segment,
                edits,
            )
        ]
        return fixes

    @staticmethod
    def _convert_fix_list(
        context: RuleContext,
        convert_arg_1: BaseSegment,
        convert_arg_2: BaseSegment,
        later_types=None,
    ) -> List[LintFix]:
        """Generate list of fixes to convert CAST and ShortHandCast to CONVERT."""
        # Add convert and opening parenthesis.
        edits = [
            KeywordSegment("convert"),
            SymbolSegment("(", type="start_bracket"),
            convert_arg_1,
            SymbolSegment(",", type="comma"),
            WhitespaceSegment(),
            convert_arg_2,
            SymbolSegment(")", type="end_bracket"),
        ]

        if later_types:
            pre_edits: List[BaseSegment] = [
                KeywordSegment("convert"),
                SymbolSegment("(", type="start_bracket"),
            ]
            in_edits: List[BaseSegment] = [
                SymbolSegment(",", type="comma"),
                WhitespaceSegment(),
            ]
            post_edits: List[BaseSegment] = [
                SymbolSegment(")", type="end_bracket"),
            ]
            for _type in later_types:
                edits = pre_edits + [_type] + in_edits + edits + post_edits

        fixes = [
            LintFix.replace(
                context.segment,
                edits,
            )
        ]
        return fixes

    @staticmethod
    def _shorthand_fix_list(
        context: RuleContext, shorthand_arg_1: BaseSegment, shorthand_arg_2: BaseSegment
    ) -> List[LintFix]:
        """Generate list of fixes to convert CAST and CONVERT to ShorthandCast."""
        edits = [
            shorthand_arg_1,
            SymbolSegment("::", type="casting_operator"),
            shorthand_arg_2,
        ]

        fixes = [
            LintFix.replace(
                context.segment,
                edits,
            )
        ]
        return fixes

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Enforce consistent type casting style."""
        # Config type hints
        self.preferred_type_casting_style: str

        # Rule disabled for teradata.
        if context.dialect.name == "teradata":
            return None

        # Construct segment type casting
        current_type_casting_style = (
            "cast"
            if context.segment.is_type("function")
            and context.segment.get_child("function_name").raw_upper == "CAST"
            else "convert"
            if context.segment.is_type("function")
            and context.segment.get_child("function_name").raw_upper == "CONVERT"
            else "shorthand"
            if context.segment.is_type("cast_expression")
            else None
        )

        # If casting style is set to consistent,
        # we use the casting style of the first segment we encounter.
        if self.preferred_type_casting_style == "consistent":
            memory = context.memory
            prior_type_casting_style = context.memory.get("prior_type_casting_style")

            # Construct fixes
            if prior_type_casting_style == "cast":
                if current_type_casting_style == "convert":
                    # Get the content of CONVERT
                    convert_content = self._get_children(
                        FunctionalContext(context).segment.children(
                            sp.is_type("bracketed")
                        )
                    )
                    # We only care about 2-arguments convert
                    # some dialects allow an optional 3rd argument e.g TSQL
                    # which cannot be rewritten into CAST
                    if len(convert_content) > 2:
                        return None

                    fixes = self._cast_fix_list(
                        context,
                        convert_content[1],
                        convert_content[0],
                    )
                elif current_type_casting_style == "shorthand":
                    # Get the expression and the datatype segment
                    expression_datatype_segment = self._get_children(
                        FunctionalContext(context).segment
                    )

                    fixes = self._cast_fix_list(
                        context,
                        expression_datatype_segment[0],
                        expression_datatype_segment[1],
                        # We can have multiple shorthandcast e.g 1::int::text
                        # in that case, we need to introduce nested CAST()
                        expression_datatype_segment[2:],
                    )

            elif prior_type_casting_style == "convert":
                if current_type_casting_style == "cast":
                    cast_content = self._get_children(
                        FunctionalContext(context).segment.children(
                            sp.is_type("bracketed")
                        )
                    )
                    fixes = self._convert_fix_list(
                        context,
                        cast_content[1],
                        cast_content[0],
                    )
                elif current_type_casting_style == "shorthand":
                    expression_datatype_segment = self._get_children(
                        FunctionalContext(context).segment
                    )
                    fixes = self._convert_fix_list(
                        context,
                        expression_datatype_segment[1],
                        expression_datatype_segment[0],
                        expression_datatype_segment[2:],
                    )
            elif prior_type_casting_style == "shorthand":
                if current_type_casting_style == "cast":
                    # Get the content of CAST
                    cast_content = self._get_children(
                        FunctionalContext(context).segment.children(
                            sp.is_type("bracketed")
                        )
                    )
                    fixes = self._shorthand_fix_list(
                        context,
                        cast_content[0],
                        cast_content[1],
                    )
                elif current_type_casting_style == "convert":
                    convert_content = self._get_children(
                        FunctionalContext(context).segment.children(
                            sp.is_type("bracketed")
                        )
                    )
                    if len(convert_content) > 2:
                        return None

                    fixes = self._shorthand_fix_list(
                        context,
                        convert_content[1],
                        convert_content[0],
                    )

            if (
                prior_type_casting_style
                and current_type_casting_style
                and (prior_type_casting_style != current_type_casting_style)
            ):
                return LintResult(
                    anchor=context.segment,
                    memory=context.memory,
                    fixes=fixes,
                    description=("Inconsistent type casting styles found."),
                )

            if prior_type_casting_style is None:
                # Only update prior_type_casting_style if it is none, this ultimately
                # makes sure we maintain the first casting style we encounter
                memory["prior_type_casting_style"] = current_type_casting_style
        elif current_type_casting_style != self.preferred_type_casting_style:
            if self.preferred_type_casting_style == "cast":
                if current_type_casting_style == "convert":
                    convert_content = self._get_children(
                        FunctionalContext(context).segment.children(
                            sp.is_type("bracketed")
                        )
                    )
                    if len(convert_content) > 2:
                        return None

                    fixes = self._cast_fix_list(
                        context,
                        convert_content[1],
                        convert_content[0],
                    )
                elif current_type_casting_style == "shorthand":
                    expression_datatype_segment = self._get_children(
                        FunctionalContext(context).segment
                    )
                    fixes = self._cast_fix_list(
                        context,
                        expression_datatype_segment[0],
                        expression_datatype_segment[1],
                        expression_datatype_segment[2:],
                    )
            elif self.preferred_type_casting_style == "convert":
                if current_type_casting_style == "cast":
                    cast_content = self._get_children(
                        FunctionalContext(context).segment.children(
                            sp.is_type("bracketed")
                        )
                    )
                    fixes = self._convert_fix_list(
                        context,
                        cast_content[1],
                        cast_content[0],
                    )
                elif current_type_casting_style == "shorthand":
                    expression_datatype_segment = self._get_children(
                        FunctionalContext(context).segment
                    )
                    fixes = self._convert_fix_list(
                        context,
                        expression_datatype_segment[1],
                        expression_datatype_segment[0],
                        expression_datatype_segment[2:],
                    )
            elif self.preferred_type_casting_style == "shorthand":
                if current_type_casting_style == "cast":
                    cast_content = self._get_children(
                        FunctionalContext(context).segment.children(
                            sp.is_type("bracketed")
                        )
                    )
                    fixes = self._shorthand_fix_list(
                        context,
                        cast_content[0],
                        cast_content[1],
                    )
                elif current_type_casting_style == "convert":
                    convert_content = self._get_children(
                        FunctionalContext(context).segment.children(
                            sp.is_type("bracketed")
                        )
                    )
                    if len(convert_content) > 2:
                        return None
                    fixes = self._shorthand_fix_list(
                        context,
                        convert_content[1],
                        convert_content[0],
                    )

            return LintResult(
                anchor=context.segment,
                memory=context.memory,
                fixes=fixes,
                description=(
                    "Used type casting style is different from the \
                    preferred type casting style."
                ),
            )
        return None
