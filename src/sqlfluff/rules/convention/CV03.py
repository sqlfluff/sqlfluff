"""Implementation of Rule CV03."""

from typing import Optional

from sqlfluff.core.parser import BaseSegment, SymbolSegment
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.functional import FunctionalContext, sp


class Rule_CV03(BaseRule):
    """Trailing commas within select clause.

    .. note::
       For many database backends this is allowed. For some users
       this may be something they wish to enforce (in line with
       Python best practice). Many database backends regard this
       as a syntax error, and as such the `SQLFluff` default is to
       forbid trailing commas in the select clause.

    **Anti-pattern**

    .. code-block:: sql

        SELECT
            a,
            b,
        FROM foo

    **Best practice**

    .. code-block:: sql

        SELECT
            a,
            b
        FROM foo
    """

    name = "convention.select_trailing_comma"
    aliases = ("L038",)
    groups = ("all", "core", "convention")
    config_keywords = ["select_clause_trailing_comma"]
    crawl_behaviour = SegmentSeekerCrawler({"select_clause"})
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Trailing commas within select clause."""
        # Config type hints
        self.select_clause_trailing_comma: str

        segment = FunctionalContext(context).segment
        children = segment.children()
        # Iterate content to find last element
        last_content: BaseSegment = children.last(sp.is_code())[0]

        # What mode are we in?
        if self.select_clause_trailing_comma == "forbid":
            # Is it a comma?
            if last_content.is_type("comma"):
                # The last content is a comma. Before we try and remove it, we
                # should check that it's safe. One edge case is that it's a trailing
                # comma in a loop, but that if we try and remove it, we also break
                # the previous examples. We should check that this comma doesn't
                # share a source position with any other commas in the same select.

                # If there isn't a source position, then it's safe to remove, it's
                # a recent addition.
                if not last_content.pos_marker:  # pragma: no cover
                    fixes = [LintFix.delete(last_content)]
                else:
                    comma_pos = last_content.pos_marker.source_position()
                    for seg in context.segment.segments:
                        if seg.is_type("comma"):
                            if not seg.pos_marker:  # pragma: no cover
                                continue
                            elif seg.pos_marker.source_position() == comma_pos:
                                if seg is not last_content:
                                    # Not safe to fix
                                    self.logger.info(
                                        "Preventing deletion of %s, because source "
                                        "position is the same as %s. Templated "
                                        "positions are %s and %s.",
                                        last_content,
                                        seg,
                                        last_content.pos_marker.templated_position(),
                                        seg.pos_marker.templated_position(),
                                    )
                                    fixes = []
                                    break
                    else:
                        # No matching commas found. It's safe.
                        fixes = [LintFix.delete(last_content)]

                return LintResult(
                    anchor=last_content,
                    fixes=fixes,
                    description="Trailing comma in select statement forbidden",
                )
        elif self.select_clause_trailing_comma == "require":
            if not last_content.is_type("comma"):
                new_comma = SymbolSegment(",", type="comma")
                return LintResult(
                    anchor=last_content,
                    fixes=[LintFix.replace(last_content, [last_content, new_comma])],
                    description="Trailing comma in select statement required",
                )
        return None
