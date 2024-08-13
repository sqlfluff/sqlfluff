"""Implementation of Rule AL01."""

from typing import Optional, Tuple, cast

from sqlfluff.core.parser import (
    BaseSegment,
    KeywordSegment,
    RawSegment,
)
from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.reflow import ReflowSequence


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
    groups: Tuple[str, ...] = ("all", "aliasing")
    config_keywords = ["aliasing"]
    crawl_behaviour = SegmentSeekerCrawler({"alias_expression"}, provide_raw_stack=True)
    is_fix_compatible = True

    _target_parent_types: Tuple[str, ...] = (
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
            as_keyword: Optional[BaseSegment]
            for as_keyword in context.segment.segments:
                if as_keyword.raw_upper == "AS":
                    break
            else:
                as_keyword = None

            if as_keyword:
                if self.aliasing == "implicit":
                    self.logger.debug("Removing AS keyword and respacing.")
                    return LintResult(
                        anchor=as_keyword,
                        # Generate the fixes to remove and respace accordingly.
                        fixes=ReflowSequence.from_around_target(
                            as_keyword,
                            context.parent_stack[0],
                            config=context.config,
                        )
                        .without(cast(RawSegment, as_keyword))
                        .respace()
                        .get_fixes(),
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
                return LintResult(
                    anchor=context.segment,
                    # Work out the insertion and reflow fixes.
                    fixes=ReflowSequence.from_around_target(
                        identifier,
                        context.parent_stack[0],
                        config=context.config,
                        # Only reflow before, otherwise we catch too much.
                        sides="before",
                    )
                    .insert(
                        KeywordSegment("AS"),
                        target=identifier,
                        pos="before",
                    )
                    .respace()
                    .get_fixes(),
                )
        return None
