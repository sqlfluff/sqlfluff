"""Implementation of Rule TQ04."""

from typing import Optional

from sqlfluff.core.parser import BaseSegment, KeywordSegment, WhitespaceSegment
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.dialects.dialect_ansi import AsAliasOperatorSegment


class Rule_TQ04(BaseRule):
    """Prefer ANSI-style ``AS`` aliasing over ``alias = expression`` in T-SQL.

    T-SQL supports an alternative alias form in ``SELECT`` clauses using
    ``alias = expression``. This rule enforces the more ANSI-style
    ``expression AS alias`` form instead.

    This rule only applies to the ``tsql`` dialect and is disabled by
    default. Enable it with the ``force_enable = True`` flag.

    **Anti-pattern**

    .. code-block:: sql
       :force:

        SELECT
            help3 = 'hello',
            help4 = CASE WHEN help = 'apple' THEN 'hello' END

    **Best practice**

    .. code-block:: sql
       :force:

        SELECT
            'hello' AS help3,
            CASE WHEN help = 'apple' THEN 'hello' END AS help4
    """

    name = "tsql.prefer_as_alias"
    aliases = ()
    groups = ("all", "tsql")
    config_keywords = ["force_enable"]
    crawl_behaviour = SegmentSeekerCrawler({"alias_expression"})
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Prefer ANSI-style ``AS`` aliasing over ``alias = expression``."""
        self.force_enable: bool

        if not self.force_enable:
            return None

        if context.dialect.name != "tsql":
            return None  # pragma: no cover

        alias_expression = context.segment
        if not alias_expression.is_type("alias_expression"):  # pragma: no cover
            return None

        alias_operator = alias_expression.get_child("alias_operator")
        if getattr(alias_operator, "raw", None) != "=":
            return None

        select_clause_element = context.parent_stack[-1]
        if not select_clause_element.is_type("select_clause_element"):
            return None

        alias_identifier = next(
            (
                seg
                for seg in alias_expression.segments
                if seg.is_code and seg is not alias_operator
            ),
            None,
        )
        expression_segment = next(
            (
                seg
                for seg in select_clause_element.segments
                if seg is not alias_expression and seg.is_code
            ),
            None,
        )
        if not alias_identifier or not expression_segment:
            return None  # pragma: no cover

        as_alias_operator_segment = AsAliasOperatorSegment(
            segments=(KeywordSegment("AS"),)
        )
        edit_segments: list[BaseSegment] = [
            expression_segment,
            WhitespaceSegment(),
            as_alias_operator_segment,
            WhitespaceSegment(),
            alias_identifier,
        ]

        return LintResult(
            anchor=alias_operator,
            description="Use ANSI-style `AS` aliasing instead of `alias = expression`.",
            fixes=[
                LintFix.replace(
                    select_clause_element,
                    edit_segments,
                    source=[expression_segment, alias_identifier],
                )
            ],
        )
