"""Implementation of Rule AL01."""

from typing import Optional

from sqlfluff.core.parser import BaseSegment, KeywordSegment, WhitespaceSegment
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.dialects.dialect_ansi import AsAliasOperatorSegment


class Rule_AL01(BaseRule):
    """Implicit/explicit aliasing of table.

    Aliasing of table to follow preference
    (requiring an explicit ``AS`` is the default).

    **Anti-pattern**

    In this example, the alias ``voo`` is implicit.

    .. code-block:: sql

        SELECT
            voo.a
        FROM foo voo

    **Best practice**

    Add ``AS`` to make it explicit.

    .. code-block:: sql

        SELECT
            voo.a
        FROM foo AS voo

    """

    name = "aliasing.table"
    aliases = ("L011",)
    groups: tuple[str, ...] = ("all", "aliasing")
    config_keywords = ["aliasing"]
    crawl_behaviour = SegmentSeekerCrawler({"alias_expression"}, provide_raw_stack=True)
    is_fix_compatible = True

    _target_parent_types: tuple[str, ...] = (
        "from_expression_element",
        "merge_statement",
    )

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Implicit aliasing of table/column not allowed. Use explicit `AS` clause.

        We look for the alias segment, and then evaluate its parent and whether
        it contains an AS keyword. This is the _eval function for both AL01 and AL02.
        """
        # Config type hints
        self.aliasing: str

        # AL01 is disabled for Oracle, still run for AL02.
        if context.dialect.name == "oracle" and self.name == "aliasing.table":
            return None

        assert context.segment.is_type("alias_expression")
        if context.parent_stack[-1].is_type(*self._target_parent_types):
            # Search for an AS keyword.
            as_keyword: Optional[BaseSegment] = context.segment.get_child(
                "alias_operator"
            )

            if as_keyword:
                if self.aliasing == "implicit":
                    self.logger.debug("Removing AS keyword and respacing.")
                    whitespace: Optional[BaseSegment] = context.segment.get_child(
                        "whitespace"
                    )
                    if whitespace:
                        fixes = [LintFix.delete(whitespace), LintFix.delete(as_keyword)]
                    else:
                        fixes = [LintFix.delete(as_keyword)]  # pragma: no cover

                    return LintResult(
                        anchor=as_keyword,
                        fixes=fixes,
                    )

            elif self.aliasing != "implicit":
                self.logger.debug("Inserting AS keyword and respacing.")
                for identifier in context.segment.raw_segments:
                    if identifier.is_code:
                        break
                else:  # pragma: no cover
                    raise NotImplementedError(
                        "Failed to find identifier. Raise this as a bug on GitHub."
                    )
                as_alias_operator_segment = AsAliasOperatorSegment(
                    segments=(KeywordSegment("AS"),)
                )
                # if the pre sibling has already a leading whitespace at it's tail
                # we do not need an additional leading whitespace
                has_leading_whitespace = context.siblings_pre and isinstance(
                    context.siblings_pre[-1], WhitespaceSegment
                )
                if has_leading_whitespace:
                    edit_segments = [as_alias_operator_segment, WhitespaceSegment()]
                else:
                    edit_segments = [
                        WhitespaceSegment(),
                        as_alias_operator_segment,
                        WhitespaceSegment(),
                    ]
                return LintResult(
                    anchor=context.segment,
                    fixes=[LintFix.create_before(identifier, edit_segments)],
                )
        return None
