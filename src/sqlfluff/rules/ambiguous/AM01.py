"""Implementation of Rule AM01."""

from typing import Optional

from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.functional import FunctionalContext, sp


class Rule_AM01(BaseRule):
    """Ambiguous use of ``DISTINCT`` in a ``SELECT`` statement with ``GROUP BY``.

    When using ``GROUP BY`` a `DISTINCT`` clause should not be necessary as every
    non-distinct ``SELECT`` clause must be included in the ``GROUP BY`` clause.

    **Anti-pattern**

    ``DISTINCT`` and ``GROUP BY`` are conflicting.

    .. code-block:: sql

        SELECT DISTINCT
            a
        FROM foo
        GROUP BY a

    **Best practice**

    Remove ``DISTINCT`` or ``GROUP BY``. In our case, removing ``GROUP BY`` is better.

    .. code-block:: sql

        SELECT DISTINCT
            a
        FROM foo
    """

    name = "ambiguous.distinct"
    aliases = ("L021",)
    groups: tuple[str, ...] = ("all", "core", "ambiguous")
    crawl_behaviour = SegmentSeekerCrawler({"select_statement"})

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Ambiguous use of DISTINCT in select statement with GROUP BY."""
        segment = FunctionalContext(context).segment
        # We know it's a select_statement from the seeker crawler
        assert segment.all(sp.is_type("select_statement"))
        # Do we have a group by clause
        group_by = segment.children(sp.is_type("groupby_clause"))
        if group_by:
            # Do we have the "DISTINCT" keyword in the select clause
            modifier = segment.children(sp.is_type("select_clause")).children(
                sp.is_type("select_clause_modifier")
            )
            distinct = modifier.children(sp.is_keyword("distinct"))
            if not distinct:
                return None
            # DISTINCT ON (...) keeps one row per value of its expressions. It is
            # only redundant when every GROUP BY term is one of those expressions,
            # because the grouped rows are then already unique on that key.
            on_list = modifier.children(sp.is_type("bracketed"))
            if modifier.children(sp.is_keyword("on")) and on_list:
                group_terms = self._list_terms(group_by[0])
                if not group_terms or not group_terms <= self._list_terms(on_list[0]):
                    return None
            return LintResult(anchor=distinct[0])
        return None

    @staticmethod
    def _list_terms(segment: BaseSegment) -> set[str]:
        """Return the normalised terms of a comma separated list.

        Keywords, commas and brackets are skipped. Each term is compared by its
        upper-cased code, so whitespace, comments and case don't matter.
        """
        return {
            "".join(raw.raw_upper for raw in child.raw_segments if raw.is_code)
            for child in segment.segments
            if child.is_code
            and not child.is_type("keyword", "comma", "start_bracket", "end_bracket")
        }
