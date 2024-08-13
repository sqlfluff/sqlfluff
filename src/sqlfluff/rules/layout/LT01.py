"""Implementation of Rule LT01."""

from typing import List, Optional

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import RootOnlyCrawler
from sqlfluff.utils.reflow.sequence import ReflowSequence


class Rule_LT01(BaseRule):
    """Inappropriate Spacing.

    This rule checks for an enforces the spacing as configured in
    :ref:`layoutconfig`. This includes excessive whitespace,
    trailing whitespace at the end of a line and also the wrong
    spacing between elements on the line. Because of this wide reach
    you may find that you wish to add specific configuration in your
    project to tweak how specific elements are treated. Rather than
    configuration on this specific rule, use the `sqlfluff.layout`
    section of your configuration file to customise how this rule
    operates.

    The ``•`` character represents a space in the examples below.

    **Anti-pattern**

    .. code-block:: sql
        :force:

        SELECT
            a,        b(c) as d••
        FROM foo••••
        JOIN bar USING(a)

    **Best practice**

    * Unless an indent or preceding a comment, whitespace should
      be a single space.

    * There should also be no trailing whitespace at the ends of lines.

    * There should be a space after :code:`USING` so that it's not confused
      for a function.

    .. code-block:: sql

        SELECT
            a, b(c) as d
        FROM foo
        JOIN bar USING (a)
    """

    name = "layout.spacing"
    # NOTE: This rule combines the following legacy rules:
    # - L001: Trailing Whitespace
    # - L005 & L008: Space around commas
    # - L006: Space around operators
    # - L023: Space after AS in WITH clause
    # - L024: Space immediately after USING
    # - L039: Unnecessary Whitespace
    # - L048: Spacing around quoted literals
    # - L071: Spacing around brackets
    aliases = ("L001", "L005", "L006", "L008", "L023", "L024", "L039", "L048", "L071")
    groups = ("all", "core", "layout")
    crawl_behaviour = RootOnlyCrawler()
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> Optional[List[LintResult]]:
        """Unnecessary whitespace."""
        sequence = ReflowSequence.from_root(context.segment, config=context.config)
        return sequence.respace().get_results()
