"""Implementation of Rule L011."""
from typing import List, Optional, Tuple

from sqlfluff.core.parser import (
    KeywordSegment,
)

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
    document_groups,
)
from sqlfluff.utils.reflow import ReflowSequence


@document_groups
@document_fix_compatible
@document_configuration
class Rule_L011(BaseRule):
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

    groups: Tuple[str, ...] = ("all",)
    config_keywords = ["aliasing"]
    crawl_behaviour = SegmentSeekerCrawler({"alias_expression"}, provide_raw_stack=True)

    _target_elems: List[Tuple[str, str]] = [
        ("type", "from_expression_element"),
        ("type", "merge_statement"),
    ]

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Implicit aliasing of table/column not allowed. Use explicit `AS` clause.

        We look for the alias segment, and then evaluate its parent and whether
        it contains an AS keyword. This is the _eval function for both L011 and L012.
        """
        # Config type hints
        self.aliasing: str

        assert context.segment.is_type("alias_expression")
        if self.matches_target_tuples(context.parent_stack[-1], self._target_elems):
            if any(e.raw_upper == "AS" for e in context.segment.segments):
                if self.aliasing == "implicit":
                    if context.segment.segments[0].raw_upper == "AS":
                        self.logger.debug("Removing AS keyword and respacing.")
                        as_keyword = context.segment.segments[0]
                        return LintResult(
                            anchor=as_keyword,
                            # Generate the fixes to remove and respace accordingly.
                            fixes=ReflowSequence.from_around_target(
                                as_keyword,
                                context.parent_stack[0],
                                config=context.config,
                            )
                            .without(as_keyword)
                            .respace()
                            .get_fixes(),
                        )

            elif self.aliasing != "implicit":
                self.logger.debug("Inserting AS keyword and respacing.")
                return LintResult(
                    anchor=context.segment,
                    # Work out the insertion and reflow fixes.
                    fixes=ReflowSequence.from_around_target(
                        context.segment.raw_segments[0],
                        context.parent_stack[0],
                        config=context.config,
                        # Only reflow before, otherwise we catch too much.
                        sides="before",
                    )
                    .insert(
                        KeywordSegment("AS"),
                        target=context.segment.raw_segments[0],
                        pos="before",
                    )
                    .respace()
                    .get_fixes(),
                )
        return None
