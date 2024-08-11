"""Implementation of Rule CV07."""

from typing import List

from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import RootOnlyCrawler
from sqlfluff.utils.functional import Segments, sp


class Rule_CV07(BaseRule):
    """Top-level statements should not be wrapped in brackets.

    **Anti-pattern**

    A top-level statement is wrapped in brackets.

    .. code-block:: sql
       :force:

        (SELECT
            foo
        FROM bar)

        -- This also applies to statements containing a sub-query.

        (SELECT
            foo
        FROM (SELECT * FROM bar))

    **Best practice**

    Don't wrap top-level statements in brackets.

    .. code-block:: sql
       :force:

        SELECT
            foo
        FROM bar

        -- Likewise for statements containing a sub-query.

        SELECT
            foo
        FROM (SELECT * FROM bar)
    """

    name = "convention.statement_brackets"
    aliases = ("L053",)
    groups = ("all", "convention")
    crawl_behaviour = RootOnlyCrawler()
    is_fix_compatible = True

    @staticmethod
    def _iter_statements(file_segment):
        """Designed to be used on files.

        Yields only direct children, or children of batches.
        """
        for seg in file_segment.segments:
            if seg.is_type("batch"):
                for subseg in seg.segments:
                    if subseg.is_type("statement"):
                        yield subseg
            elif seg.is_type("statement"):
                yield seg

    @classmethod
    def _iter_bracketed_statements(cls, file_segment):
        for stmt in cls._iter_statements(file_segment):
            for seg in stmt.segments:
                if seg.is_type("bracketed"):
                    yield stmt, seg

    def _eval(self, context: RuleContext) -> List[LintResult]:
        """Top-level statements should not be wrapped in brackets."""
        # Because of the root_only_crawler, this can control its own
        # crawling behaviour.
        results = []
        for parent, bracketed_segment in self._iter_bracketed_statements(
            context.segment
        ):
            self.logger.debug("Evaluating %s in %s", bracketed_segment, parent)
            # Replace the bracketed segment with it's
            # children, excluding the bracket symbols.
            bracket_set = {"start_bracket", "end_bracket"}

            filtered_children = Segments(
                *[
                    segment
                    for segment in bracketed_segment.segments
                    if segment.get_type() not in bracket_set and not segment.is_meta
                ]
            )

            # Lift leading/trailing whitespace and inline comments to the
            # segment above. This avoids introducing a parse error (ANSI and other
            # dialects generally don't allow this at lower levels of the parse
            # tree).
            to_lift_predicate = sp.or_(sp.is_whitespace(), sp.is_type("inline_comment"))
            leading = filtered_children.select(loop_while=to_lift_predicate)
            self.logger.debug("Leading: %s", leading)
            trailing = (
                filtered_children.reversed()
                .select(loop_while=to_lift_predicate)
                .reversed()
            )
            self.logger.debug("Trailing: %s", trailing)
            lift_nodes = set(leading + trailing)
            fixes = []
            if lift_nodes:
                fixes.append(LintFix.create_before(parent, list(leading)))
                fixes.append(LintFix.create_after(parent, list(trailing)))
                fixes.extend([LintFix.delete(segment) for segment in lift_nodes])
                filtered_children = filtered_children[len(leading) : -len(trailing)]

            fixes.append(
                LintFix.replace(
                    bracketed_segment,
                    filtered_children,
                )
            )

            results.append(LintResult(anchor=bracketed_segment, fixes=fixes))
        return results
